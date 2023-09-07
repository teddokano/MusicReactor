from machine import Pin, ADC, Timer
import	utime
import	sys

from	machine		import	I2C
from	nxp_periph	import	PCA9955B, LED, PCA9629A, I2C_target

if "MicroPython v1.19" in sys.version:
	TIMER_ID	= 0
else:
	TIMER_ID	= -1

class periodic_adc:
	def __init__( self, pin_name = "A0", *, interval = 10, scaling = (2 ** 16) ):
		self.timer_flag	= False
		self.adc		= ADC( Pin( pin_name ) )
		self.scaling	= scaling
		self.interval	= interval

		self.tim	= Timer( TIMER_ID )
		self.tim.init( period = interval, mode = Timer.PERIODIC, callback = self.timer_callback )

	def read( self ):
		while True:
			while not self.timer_flag:
				pass

			self.timer_flag	= False
					
			yield self.adc.read_u16() / self.scaling

	def timer_callback( self, _ ):
		self.timer_flag	= True

class peak_detect( periodic_adc ):
	def __init__( self, pin_name = "A0", *, interval = 10, scaling = (2 ** 16), threshold_half_life = 350, ignore_interval = 50, squelch = 0.02 ):
		super().__init__( interval = interval, scaling = scaling )
		self.det_lev_decay			= 0.5 ** (1 / (threshold_half_life / interval))
		self.det_ignore_interval	= ignore_interval / interval
		self.squelch				= squelch
		
		self.count		= 0
		self.ref_level	= 0
		self.last_count	= 0
		self.det		= False

		self.prev_level	= 0
		
		self.ovld	= Pin( "D7", Pin.OUT )

	def detect( self ):
		for read_value in self.read():
		
			level	= read_value - self.prev_level
			self.prev_level	= read_value
			
			if read_value < 0.4:
				self.ovld.value( 0 )
			else:
				self.ovld.value( 1 )

		"""	
		if self.count < self.det_ignore_interval:
			self.count		+= 1
			self.det		= False
			
			return	self.det
		"""
			if (self.ref_level < level) and (self.squelch < level):
				self.last_count	= self.count
				self.count		= 0
				self.det		= True
				self.ref_level	= level
				
				#print( self.last_count )
			else:	
				self.count	+= 1
				self.det	= False
			
			self.ref_level	*= self.det_lev_decay
			
			yield self.det

class motor:
	def __init__( self, i2c ):
		self.motor		= PCA9629A( i2c, address = 0xE0 >> 1 )
		
		self.direction	= False
		self.motor.stop()
		self.motor.home()
		utime.sleep( 2 )

		self.motor.write_registers( "MSK", 0x1F )

		self.motor.drv_phase( 0.5 )	# 0.5 = half_step, 1 = 1_phase, 2 = 2_phase

		self.motor.pps( 96 )
		self.motor.pps( 96, reverse = True )
		self.motor.steps( 192 )
		self.motor.steps( 192, reverse = True )
		self.prev_time	= 0

	def start( self ):
		self.motor.start()
	
	def invert( self ):
		now	= utime.ticks_ms()
		
		if (now - self.prev_time) > 150:
			self.direction	= False if self.direction else True
			self.motor.stop()
			self.motor.start( reverse = self.direction )
	
		self.prev_time	= now

class General_call( I2C_target ):
	def __init__( self, i2c ):
		super().__init__( i2c, 0 )
		
	def reset( self ):
		self.live	= True
		self.write_registers( 0x06, [] )

	def reprogram( self ):
		self.live	= True
		self.write_registers( 0x04, [] )

def main():
	i2c		= I2C( 0, freq = (100 * 1000) )
	
	print( i2c.scan() )
	
	gene	= General_call( i2c )
	gene.reset()

	led_c	= PCA9955B( i2c, 0xEC >>1, iref = 0xFF )
	led_c.bit_operation( "MODE1", 0x01, 0x00 )

	mtr		= motor( i2c )
	
	
	leds	= [ LED( led_c, i ) for i in range( led_c.CHANNELS ) ]

	peak	= peak_detect( "A0", interval = 10, threshold_half_life = 200, ignore_interval = 0 )
	
	enabling_channel	= [ x for x in range( 16 ) ]
	groups				= [ [ 1, 6, 11, 13 ], [ 2, 7, 9, 14 ], [ 3, 5, 10, 15 ], [ 0, 4, 8, 12 ] ]
		
	all	= [ 1.0 for i in range( led_c.CHANNELS ) ]
	led_c.pwm( all )

	led_c.gradation_channel_enable( enabling_channel )
	led_c.gradation_group_assign( groups )

	ramp_time	= 1.0
	off_time	= ramp_time

	#	RGB gradation on group 0, 1, 2
	rgb_cycle_time	= led_c.set_gradation( 0, 1.0, ramp_time, up = True, down = True, on = 0, off = off_time )
	led_c.set_gradation( 1, 1.0, ramp_time, up = True, down = True, on = 0, off = off_time )
	led_c.set_gradation( 2, 1.0, ramp_time, up = True, down = True, on = 0, off = off_time )

	print( f"rgb_cycle_time = {rgb_cycle_time}" )

	#	White gradation on group 3
	white_cycle_time	= led_c.set_gradation( 3, 1, 0.3, up = False, down = True, on = 0, off = 0 )

	led_c.gradation_start( 0 )
	utime.sleep( rgb_cycle_time / 3 )
	led_c.gradation_start( 1 )
	utime.sleep( rgb_cycle_time / 3 )
	led_c.gradation_start( 2 )

	mtr.start()

	vp	= 0
	for det in peak.detect():
		print( det )
		if det:
			led_c.gradation_stop( 3 )
			led_c.gradation_start( 3, continuous = False )
			vp	= 1.0
			mtr.invert()
			
		led_c.write_registers( "PWMALL", int( vp * 255.0 ) )
		
		vp	*= 0.9
		
		vp	= 0.1 if vp < 0.1 else vp

if __name__ == "__main__":
	main()

