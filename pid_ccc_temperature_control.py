# pid_ccc_temperature_control.py

import appdaemon.plugins.hass.hassapi as hass
from simple_pid import PID
import datetime

class PIDTemperatureAndHumidityControl(hass.Hass):
    def initialize(self):
        self.log("PIDTemperatureAndHumidityControl: Initialization complete")
        
        # Configuration parameters
        self.enabled = self.args.get("enabled", True)
        self.heater_enabled = self.args.get("heater_enabled", True)
        self.control_interval = self.args.get("control_interval", 5)  # seconds
        self.summary_interval = self.args.get("summary_interval", 60)  # seconds
        
        # Temperature PID settings
        self.target_temp = self.args.get("target_temp", 65.0)  # Desired temperature in °F
        self.kp = self.args.get("kp", 1.5)
        self.ki = self.args.get("ki", 0.4)
        self.kd = self.args.get("kd", 0.2)
        
        # Humidity settings
        self.target_humidity = self.args.get("target_humidity", 60.0)  # Desired humidity in %
        self.hum_upper_limit = self.args.get("hum_upper_limit", 61.0)
        self.hum_lower_limit = self.args.get("hum_lower_limit", 59.0)
        self.hum_failsafe_limit = self.args.get("hum_failsafe_limit", 62.0)
        
        # VPD settings
        self.target_vpd_low = self.args.get("target_vpd_low", 0.8)  # in kPa
        self.target_vpd_high = self.args.get("target_vpd_high", 1.2)  # in kPa
        self.vpd_kp = self.args.get("vpd_kp", 1.5)
        self.vpd_ki = self.args.get("vpd_ki", 0.3)
        self.vpd_kd = self.args.get("vpd_kd", 0.05)
        
        # Temperature failsafe settings
        self.upper_limit = self.args.get("upper_limit", 62.0)  # Force cooler ON at or above this temp in °F
        self.lower_limit = self.args.get("lower_limit", 55.0)  # Force cooler OFF at or below this temp in °F
        
        # Short-cycle protection settings
        self.min_on_time = self.args.get("min_on_time", 30)  # Minimum ON time in seconds
        self.min_off_time = self.args.get("min_off_time", 20)  # Minimum OFF time in seconds
        
        # Cooling load tracking settings
        self.cooling_load_tracking = self.args.get("cooling_load_tracking", True)
        self.cooling_threshold = self.args.get("cooling_threshold", 600)  # in seconds (10 minutes)
        self.cooler_on_start_time = None  # Timestamp when cooler was turned on
        
        # Entities configuration
        self.cooler_entity = self.args.get("cooler_entity")
        self.heater_entity = self.args.get("heater_entity")
        self.dehum_1 = self.args.get("dehum_1")
        self.dehum_2 = self.args.get("dehum_2")
        
        # Sensors configuration
        self.temp_sensor = self.args.get("temp_sensor")
        self.hum_sensor = self.args.get("hum_sensor")
        self.vpd_sensor = self.args.get("vpd_sensor")
        
        # Heater control thresholds
        self.activate_hum_threshold = self.args.get("activate_hum_threshold", 65.0)  # in %
        self.deactivate_hum_threshold = self.args.get("deactivate_hum_threshold", 62.0)  # in %
        self.activate_temp_threshold = self.args.get("activate_temp_threshold", 55.0)  # in °F
        self.deactivate_temp_threshold = self.args.get("deactivate_temp_threshold", 58.0)  # in °F
        
        # Initialize PID controllers for temperature
        self.temp_pid = PID(self.kp, self.ki, self.kd, setpoint=self.target_temp)
        self.temp_pid.output_limits = (0, 100)  # Adjust based on your control logic
        
        # Initialize other variables
        self.last_control_time = datetime.datetime.now()
        self.last_summary_time = datetime.datetime.now()
        
        # Listen to state changes on temperature and humidity sensors
        self.listen_state(self.temperature_changed, self.temp_sensor)
        self.listen_state(self.humidity_changed, self.hum_sensor)
        
        # Periodic control callback
        self.run_every(self.control_callback, datetime.datetime.now(), self.control_interval)
        
    def temperature_changed(self, entity, attribute, old, new, kwargs):
        self.log(f"Temperature changed: {new}°F")
        self.control_heating_and_cooling()
        
    def humidity_changed(self, entity, attribute, old, new, kwargs):
        self.log(f"Humidity changed: {new}%")
        self.control_heating_and_cooling()
        
    def control_callback(self, kwargs):
        self.log("Periodic control callback triggered")
        self.control_heating_and_cooling()
        
    def control_heating_and_cooling(self):
        if not self.enabled:
            self.log("App is disabled. Skipping control actions.")
            return
        
        # Get current sensor states
        temp = self.get_state(self.temp_sensor, attribute="state")
        hum = self.get_state(self.hum_sensor, attribute="state")
        
        if temp is None or hum is None:
            self.log("Temperature or Humidity sensor state is unavailable.")
            return
        
        try:
            temp = float(temp)
            hum = float(hum)
        except ValueError:
            self.log("Temperature or Humidity sensor state is not a valid float.")
            return
        
        # Heater Control Logic
        # Heater should be ON if:
        #   - Humidity >= 65%
        #   - OR Temperature < 55F
        # Heater should be OFF if:
        #   - Humidity < 62%
        #   - OR Temperature > 58F
        
        heater_should_be_on = False
        heater_should_be_off = False
        
        if hum >= self.activate_hum_threshold or temp < self.activate_temp_threshold:
            heater_should_be_on = True
            self.log(f"Heater activation condition met: Humidity={hum}% >= {self.activate_hum_threshold}% OR Temperature={temp}°F < {self.activate_temp_threshold}°F")
        if hum < self.deactivate_hum_threshold or temp > self.deactivate_temp_threshold:
            heater_should_be_off = True
            self.log(f"Heater deactivation condition met: Humidity={hum}% < {self.deactivate_hum_threshold}% OR Temperature={temp}°F > {self.deactivate_temp_threshold}°F")
        
        # Apply Heater Controls
        if heater_should_be_on:
            self.turn_on_heater()
        elif heater_should_be_off:
            self.turn_off_heater()
        else:
            self.log(f"No change in heater state. Current Temperature={temp}°F, Humidity={hum}%")
        
        # Cooling Load Tracking
        if self.cooling_load_tracking and self.cooler_entity:
            if self.get_state(self.cooler_entity) == "on":
                if not self.cooler_on_start_time:
                    # Record the time when cooler was turned on
                    self.cooler_on_start_time = datetime.datetime.now()
                    self.log(f"Cooling Load Tracking: Cooler turned ON at {self.cooler_on_start_time}")
                else:
                    # Calculate duration
                    now = datetime.datetime.now()
                    duration = (now - self.cooler_on_start_time).total_seconds()
                    self.log(f"Cooling Load Tracking: Cooler has been ON for {duration:.2f} seconds")
                    if duration > self.cooling_threshold:
                        self.log(f"Cooling Load Tracking: Cooler has exceeded threshold of {self.cooling_threshold} seconds. Taking action.")
                        self.handle_cooling_threshold_exceeded()
            else:
                if self.cooler_on_start_time:
                    self.log(f"Cooling Load Tracking: Cooler turned OFF at {datetime.datetime.now()}")
                    self.cooler_on_start_time = None  # Reset the start time
        
        # PID control for temperature
        pid_output = self.temp_pid(temp)
        error = self.temp_pid.setpoint - temp
        proportional = self.kp * error
        integral = self.ki * self.temp_pid._integral
        derivative = self.kd * self.temp_pid._last_error
        self.log(f"PID Calculations: Error={error:.2f}, Proportional={proportional:.2f}, Integral={integral:.2f}, Derivative={derivative:.2f}, Output={pid_output:.2f}")
        
        # Determine cooler state based on PID output and limits
        if temp >= self.upper_limit:
            self.log(f"Temperature={temp}°F >= upper_limit={self.upper_limit}°F. Turning cooler ON.")
            self.turn_on_cooler()
        elif temp <= self.lower_limit:
            self.log(f"Temperature={temp}°F <= lower_limit={self.lower_limit}°F. Turning cooler OFF.")
            self.turn_off_cooler()
        else:
            # Control cooler based on PID output
            if pid_output > 50:
                self.log(f"PID output={pid_output:.2f} > 50. Turning cooler ON.")
                self.turn_on_cooler()
            else:
                self.log(f"PID output={pid_output:.2f} <= 50. Turning cooler OFF.")
                self.turn_off_cooler()
        
        # Humidity control
        if hum > self.hum_failsafe_limit:
            self.log(f"Humidity={hum}% exceeds failsafe limit={self.hum_failsafe_limit}%. Activating dehumidifiers.")
            self.activate_dehumidifiers()
        elif hum < self.hum_lower_limit:
            self.log(f"Humidity={hum}% below lower limit={self.hum_lower_limit}%. Turning off dehumidifiers.")
            self.turn_off_dehumidifiers()
    
    def turn_on_heater(self):
        if self.heater_enabled and self.heater_entity:
            if self.get_state(self.heater_entity) != "on":
                self.turn_on(self.heater_entity)
                self.log(f"Heater {self.heater_entity} turned ON")
            else:
                self.log(f"Heater {self.heater_entity} is already ON")
        else:
            self.log("Heater is not enabled or heater_entity is not configured.")
        
    def turn_off_heater(self):
        if self.heater_enabled and self.heater_entity:
            if self.get_state(self.heater_entity) != "off":
                self.turn_off(self.heater_entity)
                self.log(f"Heater {self.heater_entity} turned OFF")
            else:
                self.log(f"Heater {self.heater_entity} is already OFF")
        else:
            self.log("Heater is not enabled or heater_entity is not configured.")
        
    def turn_on_cooler(self):
        if self.cooler_entity:
            if self.get_state(self.cooler_entity) != "on":
                self.turn_on(self.cooler_entity)
                self.log(f"Cooler {self.cooler_entity} turned ON")
            else:
                self.log(f"Cooler {self.cooler_entity} is already ON")
        else:
            self.log("Cooler entity is not configured.")
        
    def turn_off_cooler(self):
        if self.cooler_entity:
            if self.get_state(self.cooler_entity) != "off":
                self.turn_off(self.cooler_entity)
                self.log(f"Cooler {self.cooler_entity} turned OFF")
            else:
                self.log(f"Cooler {self.cooler_entity} is already OFF")
        else:
            self.log("Cooler entity is not configured.")
        
    def activate_dehumidifiers(self):
        if self.dehum_1 and self.dehum_2:
            if self.get_state(self.dehum_1) != "on":
                self.turn_on(self.dehum_1)
                self.log(f"Dehumidifier {self.dehum_1} turned ON")
            if self.get_state(self.dehum_2) != "on":
                self.turn_on(self.dehum_2)
                self.log(f"Dehumidifier {self.dehum_2} turned ON")
        else:
            self.log("Dehumidifier entities are not configured.")
        
    def turn_off_dehumidifiers(self):
        if self.dehum_1 and self.dehum_2:
            if self.get_state(self.dehum_1) != "off":
                self.turn_off(self.dehum_1)
                self.log(f"Dehumidifier {self.dehum_1} turned OFF")
            if self.get_state(self.dehum_2) != "off":
                self.turn_off(self.dehum_2)
                self.log(f"Dehumidifier {self.dehum_2} turned OFF")
        else:
            self.log("Dehumidifier entities are not configured.")
    
    def handle_cooling_threshold_exceeded(self):
        """
        Action to take when cooling threshold is exceeded.
        This could include:
        - Turning OFF the cooler to prevent overuse.
        - Sending notifications.
        - Implementing cooldown periods before allowing the cooler to turn ON again.
        """
        self.log(f"Cooling Load Tracking: Cooling threshold of {self.cooling_threshold} seconds exceeded.")
        # Example Action: Turn OFF Cooler
        self.turn_off_cooler()
        # Example Action: Send Notification (Ensure you have a notifier configured)
        # self.notify(f"Cooling threshold of {self.cooling_threshold/60} minutes exceeded. Cooler has been turned OFF to prevent overuse.", name="notify")
        # Reset the start time to prevent repeated actions
        self.cooler_on_start_time = None
