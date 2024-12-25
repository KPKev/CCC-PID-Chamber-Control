# CCC-PID-Chamber-Control
AppDaemon Temperature and Humidity Control
A robust AppDaemon application for Home Assistant that automates heating, cooling, and dehumidifying systems based on real-time temperature and humidity readings. This setup ensures optimal environmental conditions while maintaining energy efficiency and equipment longevity.



📋 Table of Contents
📖 Introduction
🌟 Features
🚀 Installation
🛠️ Prerequisites
📥 Cloning the Repository
🔧 Configuration
🎛️ Configuration Details
apps.yaml
Python Scripts
🛠️ Usage
🔄 Starting AppDaemon
📈 Monitoring
🔍 Cooling Load Tracking
📝 Logging Enhancements
🛠️ Troubleshooting
🤝 Contributing
📄 License
📞 Contact
📖 Introduction
Managing environmental conditions in controlled spaces such as greenhouses, indoor gardens, or server rooms is crucial for maintaining optimal performance and preventing equipment damage. This AppDaemon application leverages Home Assistant's capabilities to automate the control of heaters, coolers, and dehumidifiers based on real-time sensor data.

🌟 Features
Automated Heater Control:

Turn ON when:
Humidity ≥ 65%, OR
Temperature < 55°F
Turn OFF when:
Humidity < 62%, OR
Temperature > 58°F
PID-Based Cooler Control:

Maintains desired temperature using Proportional-Integral-Derivative (PID) algorithms.
Dynamically adjusts cooler operation based on temperature trends.
Cooling Load Tracking:

Monitors cooler operation duration to prevent continuous running beyond a set threshold (e.g., 10 minutes).
Automatically turns off the cooler if the threshold is exceeded, preventing equipment strain.
Dehumidifier Management:

Activates dehumidifiers when humidity exceeds failsafe limits.
Deactivates dehumidifiers when humidity falls below lower limits.
Comprehensive Logging:

Detailed logs for monitoring heater and cooler states, PID calculations, and cooling load tracking.
Facilitates easy troubleshooting and performance assessment.
🚀 Installation
🛠️ Prerequisites
Home Assistant: Ensure you have a running Home Assistant instance.
AppDaemon: Installed and configured as an add-on or standalone instance.
Git: To clone the repository.
Python Packages: simple-pid is required for PID-based cooler control.
📥 Cloning the Repository
Clone the repository to your local machine or directly to your Home Assistant's configuration directory.

bash
Copy code
git clone https://github.com/your-username/your-repo-name.git
🔧 Configuration
1. apps.yaml
Configure AppDaemon by updating the appdaemon.yaml file. Replace placeholders with your actual settings.

yaml
Copy code
# apps.yaml
  pid_temperature_and_humidity_control:
    module: pid_ccc_temperature_control
    class: PIDTemperatureAndHumidityControl

    # Control Settings
    enabled: true
    heater_enabled: true
    control_interval: 5  # in seconds
    summary_interval: 60  # in seconds

    # Temperature Settings
    activate_temp_threshold: 55.0  # in °F
    deactivate_temp_threshold: 58.0  # in °F

    # Humidity Settings
    activate_hum_threshold: 65.0  # in %
    deactivate_hum_threshold: 62.0  # in %
    deactivate_hum_fail: 60.0  # in %

    # Cooling Load Tracking Settings
    cooling_load_tracking: true
    cooling_threshold: 600  # in seconds (10 minutes)

    # Entities Configuration
    cooler_entity: "switch.shelly1minig3_cc8da245848c_switch_0"
    heater_entity: "switch.temps_humidity_veg_area_heater"
    dehum_1: "switch.shelly1minig3_cc8da243dc78_switch_0"
    dehum_2: "switch.shelly1minig3_34b7dac49170_switch_0"

    # Sensors Configuration
    temp_sensor: "sensor.temps_humidity_cannabis_curing_chamber_temperature"
    hum_sensor: "sensor.temps_humidity_cannabis_curing_chamber_humidity"
    vpd_sensor: "sensor.ccc_vapor_pressure_deficit"
Note:

Replace "YOUR_LONG_LIVED_ACCESS_TOKEN" with your actual Home Assistant long-lived access token.
Update entity IDs (cooler_entity, heater_entity, dehum_1, dehum_2, temp_sensor, hum_sensor, vpd_sensor) to match your Home Assistant setup.
2. Python Scripts
Ensure the apps/ directory contains the necessary Python scripts.

apps/pid_ccc_temperature_control.py: Main application script handling heater and cooler controls.

📂 Directory Structure
Ensure your repository follows this structure:

Copy code
your-repo-name/
│
├── README.md
├── LICENSE
├── .gitignore
│
├── appdaemon.yaml
│
├── apps/
│   ├── pid_ccc_temperature_control.py
│   └── hello.py
│
└── docs/
    └── index.md
🎛️ Configuration Details
apps.yaml
The apps.yaml file is the core configuration file for script. It defines settings

Key Sections:

appdaemon:
Global AppDaemon settings such as location, timezone, directories for apps and plugins, and Python package dependencies.

plugins:
Defines the Home Assistant plugin with the necessary token and URL.

apps:
Lists the apps to be loaded, including hello_world and pid_temperature_and_humidity_control. Each app has its module, class, and specific configurations.

Python Scripts
1. apps/pid_ccc_temperature_control.py
This script manages the heating and cooling systems based on temperature and humidity readings. It utilizes PID control for the cooler and discrete threshold-based control for the heater.

Key Functionalities:

Heater Control:

Turns ON when humidity ≥ 65% or temperature < 55°F.
Turns OFF when humidity < 62% or temperature > 58°F.
Cooler Control:

Uses PID to maintain the desired temperature.
Implements cooling load tracking to prevent continuous operation beyond 10 minutes.
Dehumidifier Control:

Activates when humidity exceeds 62%.
Deactivates when humidity falls below 59%.
Cooling Load Tracking:

Monitors how long the cooler has been running.
Automatically turns off the cooler if it exceeds the cooling_threshold.
Logging:

Provides detailed logs for all operations, PID calculations, and cooling load tracking.

🛠️ Usage
🔄 Starting AppDaemon
After configuring, restart AppDaemon to apply the changes.

Via Home Assistant Interface:

Navigate to Settings → Add-ons → AppDaemon.
Click Restart.
Via Command Line (if accessible):

bash
Copy code
ha addons restart appdaemon
📈 Monitoring
AppDaemon Logs:

Access logs to monitor the application's behavior.
In Home Assistant, go to Settings → Add-ons → AppDaemon → Log.
Testing Conditions:

Use Home Assistant's Developer Tools to simulate different temperature and humidity readings.
Observe how the heater, cooler, and dehumidifiers respond based on the simulated data.
Example Log Entries:

yaml
Copy code
INFO PIDTemperatureAndHumidityControl: Initialization complete
INFO HelloWorld: Hello from AppDaemon!
INFO HelloWorld: You are now ready to run Apps!
INFO PIDTemperatureAndHumidityControl: Heater activation condition met: Humidity=66.0% >= 65.0% OR Temperature=54.0°F < 55.0°F
INFO PIDTemperatureAndHumidityControl: Heater switch.temps_humidity_veg_area_heater turned ON
INFO PIDTemperatureAndHumidityControl: Dehumidifier switch.shelly1minig3_cc8da243dc78_switch_0 turned ON
INFO PIDTemperatureAndHumidityControl: Dehumidifier switch.shelly1minig3_34b7dac49170_switch_0 turned ON
INFO PIDTemperatureAndHumidityControl: Cooling Load Tracking: Cooler turned ON at 2024-04-27 10:00:00
INFO PIDTemperatureAndHumidityControl: Cooling Load Tracking: Cooler has been ON for 300.00 seconds
INFO PIDTemperatureAndHumidityControl: PID Calculations: Error=-5.00, Proportional=-7.50, Integral=1.20, Derivative=0.50, Output=-6.80
INFO PIDTemperatureAndHumidityControl: PID output=-6.80 <= 50. Turning cooler OFF.
INFO PIDTemperatureAndHumidityControl: Cooler switch.shelly1minig3_cc8da245848c_switch_0 turned OFF
🔍 Cooling Load Tracking
Purpose: Prevents the cooler from running continuously beyond a safe operational period (e.g., 10 minutes), ensuring equipment longevity and energy efficiency.

Configuration Parameters:

cooling_load_tracking:

Type: Boolean (true or false)
Default: true
Description: Enables or disables cooling load tracking.
cooling_threshold:

Type: Integer (seconds)
Default: 600 (10 minutes)
Description: Maximum allowed continuous running time for the cooler before corrective actions are taken.
How It Works:

Monitoring:

When the cooler turns ON, the current timestamp is recorded.
The script continuously calculates the duration the cooler has been active.
Threshold Check:

If the cooler remains ON beyond the cooling_threshold, the script triggers the handle_cooling_threshold_exceeded method.
Actions Taken:
Turns OFF the cooler to prevent overuse.
Logs the action for monitoring purposes.
(Optional) Sends notifications to inform you of the corrective action.
Resetting:

When the cooler turns OFF, the start time is reset, allowing future tracking cycles.
Benefits:

Prevents Equipment Strain:
Avoids prolonged operation that can lead to wear and tear.

Energy Efficiency:
Reduces unnecessary energy consumption by limiting continuous cooling.

System Stability:
Helps maintain a balanced and stable environment without overcooling.

📝 Logging Enhancements
Detailed logging is crucial for monitoring the system's behavior and troubleshooting issues. The script provides comprehensive logs for:

Heater Operations:
Logs when the heater turns ON or OFF, along with the conditions that triggered the action.

Cooler Operations:
Logs PID calculations, cooler state changes, and cooling load tracking details.

Dehumidifier Operations:
Logs activation and deactivation based on humidity levels.

Cooling Load Tracking:
Logs the duration the cooler has been running and actions taken when thresholds are exceeded.

Example Enhanced PID Logging:

mathematica
Copy code
INFO PIDTemperatureAndHumidityControl: PID Calculations: Error=-5.00, Proportional=-7.50, Integral=1.20, Derivative=0.50, Output=-6.80
Benefits:

Transparency:
Provides clear insights into how the PID controller is adjusting the cooler.

Troubleshooting:
Facilitates easy identification of issues by tracing through detailed logs.

Performance Monitoring:
Allows you to assess the effectiveness of the PID tuning and make necessary adjustments.

🛠️ Troubleshooting
Encountering issues is common when setting up automated systems. Below are some common problems and their solutions.

❌ AppDaemon Not Starting
Cause:
Syntax errors in apps.yaml or Python scripts.

Solution:

Validate your YAML configuration using YAML Lint.
Check Python scripts for syntax errors.
Review AppDaemon logs for specific error messages.
❌ Heater/Cooler Not Responding
Cause:
Incorrect entity IDs or communication issues with Home Assistant.

Solution:

Verify that all entity IDs in apps.yaml match those in Home Assistant.
Ensure devices are online and accessible.
Check logs for any error messages related to entity control.
❌ Cooling Load Tracking Not Working
Cause:
cooling_load_tracking is disabled or incorrectly configured.

Solution:

Ensure cooling_load_tracking: true in apps.yaml.
Verify that cooling_threshold is set to a reasonable value.
Check logs to see if cooling load tracking events are being logged.
❌ PID Controller Not Stabilizing
Cause:
Incorrect PID coefficients (kp, ki, kd).

Solution:

Fine-tune PID parameters based on system response.
Start with lower values and gradually increase to achieve stability.
Monitor PID output and adjust accordingly.
