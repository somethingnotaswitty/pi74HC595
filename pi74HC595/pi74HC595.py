import RPi.GPIO as gpio


class pi74HC595:
    def __init__(
        self, DS: int = 11, ST: int = 13, SH: int = 15, OE: int = 33, daisy_chain: int = 1, PWM_FRQ: int = 100
    ):

        if not (isinstance(DS, int) or isinstance(ST, int) or isinstance(SH, int) or isinstance(OE, int)):
            raise ValueError("Pins must be int")
        elif DS < 1 or DS > 40 or ST < 1 or ST > 40 or SH < 1 or SH > 40 or OE < 1 or OE > 40:
            raise ValueError("Pins (DS, ST, SH, OE) must be within pin range")

        if not isinstance(daisy_chain, int):
            raise ValueError("daisy_chain must be int")
        elif daisy_chain < 1:
            raise ValueError("daisy_chain must be positive")

        self.data = DS  # DS
        self.parallel = ST  # ST_CP
        self.serial = SH  # SH_CP
        self.output_enable = OE # OE 
        self.pwm_frequency = PWM_FRQ # Frequency for PWM pin if used 
        self.daisy_chain = daisy_chain  # Number of 74HC595s
        self.current = [0, 0, 0, 0, 0, 0, 0, 0] * self.daisy_chain
        self._setup_board()
        self.clear()

    def _setup_board(self):
        gpio.setup(self.data, gpio.OUT)
        gpio.output(self.data, gpio.LOW)
        gpio.setup(self.parallel, gpio.OUT)
        gpio.output(self.parallel, gpio.LOW)
        gpio.setup(self.serial, gpio.OUT)
        gpio.output(self.serial, gpio.LOW)

    def _output(self):  # ST_CP
        gpio.output(self.parallel, gpio.HIGH)
        gpio.output(self.parallel, gpio.LOW)

    def _tick(self):  # SH_CP
        gpio.output(self.serial, gpio.HIGH)
        gpio.output(self.serial, gpio.LOW)

    def _set_values(self, values):
        for bit in values:
            self.current.append(bit)
            del self.current[0]
            if bit == 1:
                gpio.output(self.data, gpio.HIGH)
            elif bit == 0:
                gpio.output(self.data, gpio.LOW)
            self._tick()
        self._output()

    def set_ds(self, pin: int):
        """
        Sets the pin for the serial data input (DS)

        Returns: None

        """
        if not isinstance(pin, int):
            raise ValueError("Argument must be int")
        elif pin < 1 or pin > 40:
            raise ValueError("Argument must be within pin range")

        self.data = DS

    def set_sh(self, pin: int):
        """
        Sets the pin for the shift register clock pin (SH_CP)

        Returns: None

        """
        if not isinstance(pin, int):
            raise ValueError("Argument must be int")
        elif pin < 1 or pin > 40:
            raise ValueError("Argument must be within pin range")

        self.parallel = DS

    def set_st(self, pin: int):
        """
        Sets the pin for the storage register clock pin (ST_CP)

        Returns: None

        """
        if not isinstance(pin, int):
            raise ValueError("Argument must be int")
        elif pin < 1 or pin > 40:
            raise ValueError("Argument must be within pin range")

        self.serial = ST


    def set_pwm_pin(self, pin: int ):
        """
        Set the pin to be used for PWM

        args: int in range of PWM capable pins
            - default : pin 33 / gpio 13
            - Raspberry Pi 4 PWM pins: 12 , 32, 33, 35
            - Rapsbery Pi 3 PWM pins: 

        returns: None
        """
        if not isinstance(pin, int):
            raise ValueError("Argument must be int")
        elif pin < 1 or pin > 40:
            raise ValueError("Argument must be within pin range")
        
        self.output_enable = OE

    def set_daisy_chain(self, num: int):
        """
        Sets the the number of 74HC595s used in Daisy Chain

        Returns: None

        """
        if not isinstance(num, int):
            raise ValueError("Argument must be int")
        elif num < 1:
            raise ValueError("Argument must be positive")

        self.daisy_chain = num

    def set_by_list(self, values):
        """
        Sends values in list to the internal function

        args: [0, 1, 0,...]
            or
            [False, True, False,...]

        Returns: None

        """
        if not isinstance(values, list):
            raise ValueError("Argument must be a list")

        for i in range(len(values)):
            if values[i] == True:
                values[i] = 1
            elif values[i] == False:
                values[i] = 0
            else:
                raise ValueError("Values within list must be 1, 0, or boolean")
        self._set_values(values)

    def set_by_int(self, value: int):
        """
        Sends the int value to the internal function
            (int to binary)

        args: 1 --> 1
            0 --> 0
            12 --> 1100
            999 -- > 1111100111
            etc...

        Returns: None

        """
        if not isinstance(value, int):
            raise ValueError("Argument must be int")
        elif value < 0:
            raise ValueError("Argument cannot be negative")

        self._set_values(list(bin(value)[2:]))

    def set_by_bool(self, value: bool):
        """
        Sends the boolean value to the internal function

        args: True
            or
            False

        Returns: None

        """
        if not isinstance(value, bool):
            raise ValueError("Argument must be boolean")

        if value == True:
            self._set_values([1])
        elif value == False:
            self._set_values([0])

    def get_values(self) -> list:
        """
        Returns the values of the current 74HC595(s)

        args: None

        Returns: List of current state
            [0, 1, 0,...]

        """
        return self.current

    def set_pwn_frequency(self, value: int):
        """
        Set the frequncy for the PWM pin 

        args: int in range 0-100
                - pin outputs a square waveform with variable frequency and duty cycle.
                - This uses the software PWM generator built into the RPi.GPIO lib not hardware PWM.
                - The minimum PWM output frequency is 10 Hz. The maximum PWM output frequency is 8 KHz.
                - A duty cycle of 0 means that the waveform is always low. A duty cycle of 1 means the waveform is always high.
                - Can be any value between 0 (i.e 0%/LOW) and 100 (ie.e 100%/HIGH).

        returns: None
        """
        if not isinstance(value, int):
            raise ValueError("PWM Frequency must be an int from 0 - 100")
        elif value < 0:
            raise ValueError("PWM Frequency must be an int from 0 - 100")
        elif value > 100:
            raise ValueError("PWM Frequency must be an int from 0 - 100")
        pi_pwm = gpio.PWM(self.output_enable, value)
        pi_pwm.start(0)	 


    def clear(self):
        """
        Sets the 74HC595 back to all off

        Returns: None

        """
        self._set_values([0, 0, 0, 0, 0, 0, 0, 0] * self.daisy_chain)
