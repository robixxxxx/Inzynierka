---
config:
  layout: elk
  theme: mc
  look: classic
---
classDiagram
direction TB
    class MainController {
	    -screen
	    -font
	    -menu_view: MenuView
	    -settings_manager: SettingsManager
	    +run()
	    +run_device_discovery()
	    +run_settings()
    }
    class DeviceController {
	    -devices: List[DeviceModel]
	    -view: DeviceListView
	    -settings_manager: SettingsManager
	    +discover_devices()
	    +run()
	    -_start_vehicle_control()
    }
    class CommunicationController {
	    -device: DeviceModel
	    -control_data: ControlDataModel
	    -telemetry_data: TelemetryDataModel
	    -input_handler: InputHandler
	    +start_communication()
	    +stop_communication()
	    +run()
	    +update_control_data()
	    +get_control_data()
	    -_send_loop()
	    -_receive_loop()
    }
    class InputHandler {
	    -settings_manager: SettingsManager
	    -control_data: ControlDataModel
	    +update_control_data()
	    +initialize_joystick()
	    +update_control_data()
	    +get_axis_value()
	    -_pygame_joystick_data()
	    -_keyboard_data()
    }
    class TelemetryDataModel {
	    -speed: float
	    -acceleration_x/y/z: float
	    -voltage: float
	    -current: float
	    -wifi_signal_strength: int
	    +update()
	    +get_acceleration_x/y/z()
    }
    class ControlDataModel {
	    -gear: int
	    -steering: float
	    -throttle: float
	    -brake: float
	    -functions: List[bool]
	    +update()
	    +pack_data()
    }
    class SettingsController {
	    -settings_descriptions: dict
	    -selected_option: int
	    -running: bool
	    +run()
	    +handle_input()
	    -_handle_option()
	    -_change_resolution()
	    -_adjustfont_size()
	    -_toggle_fullscreen()
	    -_configure_controller()
	    -_update_options()
	    -_reinitialize_display()
    }
    class VideoController {
	    -stream_url: string
	    -telemetry_data: TelemetryDataModel
	    -control_data: ControlDataModel
	    +run()
	    +start_video_stream()
	    +fetch_frames()
	    +start_video_stream()
	    +update_telemetry()
	    +stop()
	    -_draw_telemetry()
	    -_load_wifi_icons()
	    -_load_battery_icons()
	    -_smooth_value()
	    -_get_wifi_icon()
	    -_get_battery_icon()
    }
    class DeviceModel {
	    -name:string
	    -ip:string
	    -control_port:int
	    -telemetry_port:int
	    +set_name()
	    +set_ip()
	    +set_control_port()
	    +set_telemetry_port()
	    +get_name()
	    +get_ip()
	    +get_control_port()
	    +get_telemetry_port()
    }
    class SettingsManager {
	    -settings_file:string
	    -axis_inversion:dict
	    -joysticks:List
	    -selected_controller_index:int
	    +initialize_joystics()
	    +load_settings()
	    +save_settings()
	    +save_settings()
	    +get()
	    +set()
	    +set_resolution()
	    +toggle_fullscreen()
	    +get_controllers()
	    +assign_mapping()
	    +get_controller_config()
	    +is_logitech_device()
	    +get_axis_inversion()
	    +set_selected_controller_index()
	    +get_selected_controller()
	    +get_controller_name()
    }
    class ConfigureControllerController {
	    -function_descriptions:dict
	    -selected_option:int
	    -is_logitech_device:bool
	    -input_handler:InputHandel()
	    +run()
	    -_assign_current_function()
	    -_toggle_axis_inversion()
	    -_change_controller()
	    -_render_view()
	    -_get_inverted_axis_value()
	    -_format_control_mappings()
    }
    class ForceFeedbackController {
	    -controller_index:int
	    -logitech_controller:LogitechController()
	    +initialize_logitech_controller()
	    +update_force_feedback()
	    +shutdown()
    }
    class ConfigureControllerView {
	    -screen:pygame.display
	    -font:pygame.font
	    -background_color:tuple
	    -text_color:tuple
	    -highlight_color:tuple
	    +render_settings()
    }
    class MenuView {
	    -screen:pygame.display
	    -font:pygame.font
	    -background_color:tuple
	    -text_color:tuple
	    -highlight_color:tuple
	    +render()
    }
    class DeviceListView {
	    -screen:pygame.display
	    -font:pygame.font
	    -background_color:tuple
	    -text_color:tuple
	    -highlight_color:tuple
	    +render()
    }
    class UntitledClass {
    }

    MainController --> DeviceController
    MainController --> SettingsController
    MainController --> MenuView
    DeviceController --> CommunicationController
    DeviceController --> VideoController
    DeviceController --> DeviceModel
    DeviceController --> DeviceListView
    CommunicationController --> InputHandler
    CommunicationController --> TelemetryDataModel
    CommunicationController --> ControlDataModel
    CommunicationController --> ForceFeedbackController
    VideoController --> TelemetryDataModel
    VideoController --> ControlDataModel
    SettingsController --> ConfigureControllerController
    SettingsController --> SettingsManager
    SettingsController --> MenuView
    ConfigureControllerController --> InputHandler
    ConfigureControllerController --> ConfigureControllerView
    CommunicationController -- UntitledClass
