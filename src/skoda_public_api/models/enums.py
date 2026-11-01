from enum import Enum


class _UnknownFallbackEnum(str, Enum):
    """Enum that maps values it does not recognize to its UNKNOWN member.

    The API documents that new values may be added at any time and that clients
    must tolerate them. Without this, a single new value anywhere in a response
    would fail validation of the whole vehicle response.
    """

    @classmethod
    def _missing_(cls, value: object) -> "_UnknownFallbackEnum | None":
        return cls.__members__.get("UNKNOWN")


class TemperatureUnit(_UnknownFallbackEnum):
    CELSIUS = "CELSIUS"
    FAHRENHEIT = "FAHRENHEIT"
    UNKNOWN = "UNKNOWN"

class OnOffState(_UnknownFallbackEnum):
    ON = "ON"
    OFF = "OFF"
    UNKNOWN = "UNKNOWN"
    UNSUPPORTED = "UNSUPPORTED"

class LockState(_UnknownFallbackEnum):
    LOCKED = "LOCKED"
    UNLOCKED = "UNLOCKED"
    UNKNOWN = "UNKNOWN"

class OpenCloseState(_UnknownFallbackEnum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    UNKNOWN = "UNKNOWN"
    UNSUPPORTED = "UNSUPPORTED"

class YesNoState(_UnknownFallbackEnum):
    YES = "YES"
    NO = "NO"
    UNKNOWN = "UNKNOWN"

class DoorsState(_UnknownFallbackEnum):
    YES = "YES"
    NO = "NO"
    TRUNK_OPENED = "TRUNK_OPENED"
    OPENED = "OPENED"
    UNKNOWN = "UNKNOWN"

class AuxiliaryHeatingState(_UnknownFallbackEnum):
    HEATING = "HEATING"
    VENTILATION = "VENTILATION"
    OFF = "OFF"
    PREHEATING = "PREHEATING"
    HEATING_AUXILIARY = "HEATING_AUXILIARY"
    UNKNOWN = "UNKNOWN"
    UNSUPPORTED = "UNSUPPORTED"

class AuxiliaryHeatingStartMode(_UnknownFallbackEnum):
    HEATING = "HEATING"
    VENTILATION = "VENTILATION"
    UNKNOWN = "UNKNOWN"
   
class VentilationState(_UnknownFallbackEnum):
    VENTILATION = "VENTILATION"
    PREHEATING = "PREHEATING"
    OFF = "OFF"
    UNKNOWN = "UNKNOWN"
    UNSUPPORTED = "UNSUPPORTED"

class HeaterSourceState(_UnknownFallbackEnum):
    AUTOMATIC = "AUTOMATIC"
    ELECTRIC = "ELECTRIC"
    UNKNOWN = "UNKNOWN"

class ChargeType(_UnknownFallbackEnum):
    AC = "AC"
    DC = "DC"
    OFF = "OFF"
    UNKNOWN = "UNKNOWN"

class ChargingState(_UnknownFallbackEnum):
    CONNECT_CABLE = "CONNECT_CABLE"
    CHARGING = "CHARGING"
    CONSERVING = "CONSERVING"
    READY_FOR_CHARGING = "READY_FOR_CHARGING"
    DISCHARGING = "DISCHARGING"
    CHARGING_INTERRUPTED = "CHARGING_INTERRUPTED"
    UNKNOWN = "UNKNOWN"

class PlugConnectionState(_UnknownFallbackEnum):
    CONNECTED = "CONNECTED"
    DISCONNECTED = "DISCONNECTED"
    UNKNOWN = "UNKNOWN"

class ChargeMode(_UnknownFallbackEnum):
    MANUAL = "MANUAL"
    TIMER = "TIMER"
    TIMER_CHARGING_WITH_CLIMATISATION = "TIMER_CHARGING_WITH_CLIMATISATION"
    PREFERRED_CHARGING_TIMES = "PREFERRED_CHARGING_TIMES"
    ONLY_OWN_CURRENT = "ONLY_OWN_CURRENT"
    IMMEDIATE_DISCHARGING = "IMMEDIATE_DISCHARGING"
    HOME_STORAGE_CHARGING = "HOME_STORAGE_CHARGING"
    UNKNOWN = "UNKNOWN"

class ChargeCareModeState(_UnknownFallbackEnum):
    ACTIVATED = "ACTIVATED"
    DEACTIVATED = "DEACTIVATED"
    UNKNOWN = "UNKNOWN"

class AutoUnlockPlugState(_UnknownFallbackEnum):
    PERMANENT = "PERMANENT"
    OFF = "OFF"
    UNKNOWN = "UNKNOWN"

class MaxChargeCurrentAcState(_UnknownFallbackEnum):
    REDUCED = "REDUCED"
    MAXIMUM = "MAXIMUM"
    UNKNOWN = "UNKNOWN"

class MovementState(_UnknownFallbackEnum):
    IN_MOTION = "IN_MOTION"
    PARKED = "PARKED"
    UNKNOWN = "UNKNOWN"

class VehicleErrorState(str, Enum):
    """Known error types reported in ``VehicleResponse.errors``.

    The API documents this list as non-exhaustive, so ``VehicleError.type``
    falls back to a plain ``str`` for values not listed here.
    """
    ACTIVE_VENTILATION_DISABLED = "ACTIVE_VENTILATION_DISABLED"
    ACTIVE_VENTILATION_UNAVAILABLE = "ACTIVE_VENTILATION_UNAVAILABLE"
    ACTIVE_VENTILATION_UNSUPPORTED = "ACTIVE_VENTILATION_UNSUPPORTED"
    AIR_CONDITIONING_DISABLED = "AIR_CONDITIONING_DISABLED"
    AIR_CONDITIONING_UNAVAILABLE = "AIR_CONDITIONING_UNAVAILABLE"
    AIR_CONDITIONING_UNSUPPORTED = "AIR_CONDITIONING_UNSUPPORTED"
    AUXILIARY_HEATING_DISABLED = "AUXILIARY_HEATING_DISABLED"
    AUXILIARY_HEATING_UNAVAILABLE = "AUXILIARY_HEATING_UNAVAILABLE"
    AUXILIARY_HEATING_UNSUPPORTED = "AUXILIARY_HEATING_UNSUPPORTED"
    CHARGING_DISABLED = "CHARGING_DISABLED"
    CHARGING_PROFILES_DISABLED = "CHARGING_PROFILES_DISABLED"
    CHARGING_PROFILES_UNAVAILABLE = "CHARGING_PROFILES_UNAVAILABLE"
    CHARGING_PROFILES_UNSUPPORTED = "CHARGING_PROFILES_UNSUPPORTED"
    CHARGING_UNAVAILABLE = "CHARGING_UNAVAILABLE"
    CHARGING_UNSUPPORTED = "CHARGING_UNSUPPORTED"
    DRIVING_RANGE_DISABLED = "DRIVING_RANGE_DISABLED"
    DRIVING_RANGE_UNAVAILABLE = "DRIVING_RANGE_UNAVAILABLE"
    DRIVING_RANGE_UNSUPPORTED = "DRIVING_RANGE_UNSUPPORTED"
    FUEL_STATUS_DISABLED = "FUEL_STATUS_DISABLED"
    FUEL_STATUS_UNAVAILABLE = "FUEL_STATUS_UNAVAILABLE"
    FUEL_STATUS_UNSUPPORTED = "FUEL_STATUS_UNSUPPORTED"
    ODOMETER_DISABLED = "ODOMETER_DISABLED"
    ODOMETER_UNAVAILABLE = "ODOMETER_UNAVAILABLE"
    ODOMETER_UNSUPPORTED = "ODOMETER_UNSUPPORTED"
    OPERATIONS_UNAVAILABLE = "OPERATIONS_UNAVAILABLE"
    PARKING_POSITION_DISABLED = "PARKING_POSITION_DISABLED"
    PARKING_POSITION_UNAVAILABLE = "PARKING_POSITION_UNAVAILABLE"
    PARKING_POSITION_UNSUPPORTED = "PARKING_POSITION_UNSUPPORTED"
    RENDER_UNAVAILABLE = "RENDER_UNAVAILABLE"
    VEHICLE_STATUS_DISABLED = "VEHICLE_STATUS_DISABLED"
    VEHICLE_STATUS_UNAVAILABLE = "VEHICLE_STATUS_UNAVAILABLE"
    VEHICLE_STATUS_UNSUPPORTED = "VEHICLE_STATUS_UNSUPPORTED"

class AirConditioningState(_UnknownFallbackEnum):
    OFF = "OFF"
    COOLING = "COOLING"
    HEATING = "HEATING"
    HEATING_AUXILIARY = "HEATING_AUXILIARY"
    VENTILATION = "VENTILATION"
    COMPLETED = "COMPLETED"
    UNKNOWN = "UNKNOWN"
    UNSUPPORTED = "UNSUPPORTED"

class VehicleOperationName(_UnknownFallbackEnum):
    """A remote operation, named after the operationId of its API endpoint."""
    START_CHARGING = "startCharging"
    STOP_CHARGING = "stopCharging"
    SET_CHARGING_LIMIT = "setChargingLimit"
    SET_CHARGE_MODE = "setChargeMode"
    UPDATE_CHARGING_PROFILE = "updateChargingProfile"
    START_AIR_CONDITIONING = "startAirConditioning"
    STOP_AIR_CONDITIONING = "stopAirConditioning"
    START_AUXILIARY_HEATING = "startAuxiliaryHeating"
    STOP_AUXILIARY_HEATING = "stopAuxiliaryHeating"
    START_ACTIVE_VENTILATION = "startActiveVentilation"
    STOP_ACTIVE_VENTILATION = "stopActiveVentilation"
    UNKNOWN = "UNKNOWN"

class VehicleCapability(str, Enum):
    """A feature or vehicle attribute that a given vehicle may or may not support."""
    STATUS = "status"
    ODOMETER = "odometer"
    PARKING_POSITION = "parking_position"
    CHARGING = "charging"
    CHARGING_PROFILES = "charging_profiles"
    AIR_CONDITIONING = "air_conditioning"
    ACTIVE_VENTILATION = "active_ventilation"
    AUXILIARY_HEATING = "auxiliary_heating"
    FUEL_STATUS = "fuel_status"
    AD_BLUE_RANGE = "ad_blue_range"
    VEHICLE_TYPE_ELECTRIC = "vehicle_type_electric"
    VEHICLE_TYPE_HYBRID = "vehicle_type_hybrid"
    VEHICLE_TYPE_GASOLINE = "vehicle_type_gasoline"
    VEHICLE_TYPE_DIESEL = "vehicle_type_diesel"
    VEHICLE_TYPE_CNG = "vehicle_type_cng"
    VEHICLE_TYPE_LPG = "vehicle_type_lpg"
    SUNROOF = "sunroof"