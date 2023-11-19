from saic_ismart_client.common_model import ApplicationData, Asn1Type, TargetBatteryCode


class OtaChrgMangDataResp(ApplicationData):
    def __init__(self):
        super().__init__('OTAChrgMangDataResp')
        self.bmsReserCtrlDspCmd: int | None = None  # INTEGER(0..255),
        self.bmsReserStHourDspCmd: int | None = None  # INTEGER(0..255),
        self.bmsReserStMintueDspCmd: int | None = None  # INTEGER(0..255),
        self.bmsReserSpHourDspCmd: int | None = None  # INTEGER(0..255),
        self.bmsReserSpMintueDspCmd: int | None = None  # INTEGER(0..255),
        self.bmsOnBdChrgTrgtSOCDspCmd: int | None = None  # INTEGER(0..255),
        self.bms_estd_elec_rng: int | None = None  # INTEGER(0..65535),
        self.bmsAltngChrgCrntDspCmd: int | None = None  # INTEGER(0..255),
        self.bmsChrgCtrlDspCmd: int | None = None  # INTEGER(0..255),
        self.chrgngRmnngTime: int | None = None  # INTEGER(0..65535),
        self.chrgngRmnngTimeV: int | None = None  # INTEGER(0..255),
        self.bmsChrgOtptCrntReq: int | None = None  # INTEGER(0..65535),
        self.bmsChrgOtptCrntReqV: int | None = None  # INTEGER(0..255) OPTIONAL,
        self.bmsPackCrnt: int | None = None  # INTEGER(0..65535),
        self.bmsPackCrntV: int | None = None  # INTEGER(0..255) OPTIONAL,
        self.bmsPackVol: int | None = None  # INTEGER(0..65535),
        self.bmsPackSOCDsp: int | None = None  # INTEGER(0..65535),
        self.bmsChrgSts: int | None = None  # INTEGER(0..255),
        self.bmsChrgSpRsn: int | None = None  # INTEGER(0..255),
        self.clstrElecRngToEPT: int | None = None  # INTEGER(0..65535),
        self.bmsPTCHeatReqDspCmd: int | None = None  # INTEGER(0..255),
        self.bmsPTCHeatResp: int | None = None  # INTEGER(0..255) OPTIONAL,
        self.ccuEleccLckCtrlDspCmd: int | None = None  # INTEGER(0..255) OPTIONAL,
        self.bmsPTCHeatSpRsn: int | None = None  # INTEGER(0..255) OPTIONAL,
        self.bmsDsChrgSpRsn: int | None = None  # INTEGER(0..255) OPTIONAL,
        self.disChrgngRmnngTime: int | None = None  # INTEGER(0..65535) OPTIONAL,
        self.disChrgngRmnngTimeV: int | None = None  # INTEGER(0..255) OPTIONAL,
        self.imcuVehElecRng: int | None = None  # INTEGER(0..65535) OPTIONAL,
        self.imcuVehElecRngV: int | None = None  # INTEGER(0..255) OPTIONAL,
        self.imcuChrgngEstdElecRng: int | None = None  # INTEGER(0..65535) OPTIONAL,
        self.imcuChrgngEstdElecRngV: int | None = None  # INTEGER(0..255) OPTIONAL,
        self.imcuDschrgngEstdElecRng: int | None = None  # INTEGER(0..65535) OPTIONAL,
        self.imcuDschrgngEstdElecRngV: int | None = None  # INTEGER(0..255) OPTIONAL,
        self.chrgngSpdngTime: int | None = None  # INTEGER(0..65535) OPTIONAL,
        self.chrgngSpdngTimeV: int | None = None  # INTEGER(0..255) OPTIONAL,
        self.chrgngAddedElecRng: int | None = None  # INTEGER(0..65535) OPTIONAL,
        self.chrgngAddedElecRngV: int | None = None  # INTEGER(0..255) OPTIONAL,
        self.onBdChrgrAltrCrntInptCrnt: int | None = None  # INTEGER(0..255) OPTIONAL,
        self.onBdChrgrAltrCrntInptVol: int | None = None  # INTEGER(0..255) OPTIONAL,
        self.ccuOnbdChrgrPlugOn: int | None = None  # INTEGER(0..255) OPTIONAL,
        self.ccuOffBdChrgrPlugOn: int | None = None  # INTEGER(0..255) OPTIONAL,
        self.chrgngDoorPosSts: int | None = None  # INTEGER(0..255) OPTIONAL,
        self.chrgngDoorOpenCnd: int | None = None  # INTEGER(0..255) OPTIONAL,
        self.chargeStatus: RvsChargingStatus | None = None  # RvsChargingStatus(1),
        self.bmsAdpPubChrgSttnDspCmd: int | None = None  # INTEGER(0..255)

    def get_data(self) -> dict:
        data = {
            'bmsReserCtrlDspCmd': self.bmsReserCtrlDspCmd,
            'bmsReserStHourDspCmd': self.bmsReserStHourDspCmd,
            'bmsReserStMintueDspCmd': self.bmsReserStMintueDspCmd,
            'bmsReserSpHourDspCmd': self.bmsReserSpHourDspCmd,
            'bmsReserSpMintueDspCmd': self.bmsReserSpMintueDspCmd,
            'bmsOnBdChrgTrgtSOCDspCmd': self.bmsOnBdChrgTrgtSOCDspCmd,
            'bmsEstdElecRng': self.bms_estd_elec_rng,
            'bmsAltngChrgCrntDspCmd': self.bmsAltngChrgCrntDspCmd,
            'bmsChrgCtrlDspCmd': self.bmsChrgCtrlDspCmd,
            'chrgngRmnngTime': self.chrgngRmnngTime,
            'chrgngRmnngTimeV': self.chrgngRmnngTimeV,
            'bmsChrgOtptCrntReq': self.bmsChrgOtptCrntReq,
            'bmsPackCrnt': self.bmsPackCrnt,
            'bmsPackVol': self.bmsPackVol,
            'bmsPackSOCDsp': self.bmsPackSOCDsp,
            'bmsChrgSts': self.bmsChrgSts,
            'bmsChrgSpRsn': self.bmsChrgSpRsn,
            'clstrElecRngToEPT': self.clstrElecRngToEPT,
            'bmsPTCHeatReqDspCmd': self.bmsPTCHeatReqDspCmd,
            'chargeStatus': self.chargeStatus.get_data(),
            'bmsAdpPubChrgSttnDspCmd': self.bmsAdpPubChrgSttnDspCmd
        }
        self.add_optional_field_to_data(data, 'bmsChrgOtptCrntReqV', self.bmsChrgOtptCrntReqV)
        self.add_optional_field_to_data(data, 'bmsPackCrntV', self.bmsPackCrntV)
        self.add_optional_field_to_data(data, 'bmsPTCHeatResp', self.bmsPTCHeatResp)
        self.add_optional_field_to_data(data, 'ccuEleccLckCtrlDspCmd', self.ccuEleccLckCtrlDspCmd)
        self.add_optional_field_to_data(data, 'bmsPTCHeatSpRsn', self.bmsPTCHeatSpRsn)
        self.add_optional_field_to_data(data, 'bmsDsChrgSpRsn', self.bmsDsChrgSpRsn)
        self.add_optional_field_to_data(data, 'disChrgngRmnngTime', self.disChrgngRmnngTime)
        self.add_optional_field_to_data(data, 'disChrgngRmnngTimeV', self.disChrgngRmnngTimeV)
        self.add_optional_field_to_data(data, 'imcuVehElecRng', self.imcuVehElecRng)
        self.add_optional_field_to_data(data, 'imcuVehElecRngV', self.imcuVehElecRngV)
        self.add_optional_field_to_data(data, 'imcuChrgngEstdElecRng', self.imcuChrgngEstdElecRng)
        self.add_optional_field_to_data(data, 'imcuChrgngEstdElecRngV', self.imcuChrgngEstdElecRngV)
        self.add_optional_field_to_data(data, 'imcuDschrgngEstdElecRng', self.imcuDschrgngEstdElecRng)
        self.add_optional_field_to_data(data, 'imcuDschrgngEstdElecRngV', self.imcuDschrgngEstdElecRngV)
        self.add_optional_field_to_data(data, 'chrgngSpdngTime', self.chrgngSpdngTime)
        self.add_optional_field_to_data(data, 'chrgngSpdngTimeV', self.chrgngSpdngTimeV)
        self.add_optional_field_to_data(data, 'chrgngAddedElecRng', self.chrgngAddedElecRng)
        self.add_optional_field_to_data(data, 'chrgngAddedElecRngV', self.chrgngAddedElecRngV)
        self.add_optional_field_to_data(data, 'onBdChrgrAltrCrntInptCrnt', self.onBdChrgrAltrCrntInptCrnt)
        self.add_optional_field_to_data(data, 'onBdChrgrAltrCrntInptVol', self.onBdChrgrAltrCrntInptVol)
        self.add_optional_field_to_data(data, 'ccuOnbdChrgrPlugOn', self.ccuOnbdChrgrPlugOn)
        self.add_optional_field_to_data(data, 'ccuOffBdChrgrPlugOn', self.ccuOffBdChrgrPlugOn)
        self.add_optional_field_to_data(data, 'chrgngDoorPosSts', self.chrgngDoorPosSts)
        self.add_optional_field_to_data(data, 'chrgngDoorOpenCnd', self.chrgngDoorOpenCnd)
        return data

    def init_from_dict(self, data: dict):
        self.bmsReserCtrlDspCmd = data.get('bmsReserCtrlDspCmd')
        self.bmsReserStHourDspCmd = data.get('bmsReserStHourDspCmd')
        self.bmsReserStMintueDspCmd = data.get('bmsReserStMintueDspCmd')
        self.bmsReserSpHourDspCmd = data.get('bmsReserSpHourDspCmd')
        self.bmsReserSpMintueDspCmd = data.get('bmsReserSpMintueDspCmd')
        self.bmsOnBdChrgTrgtSOCDspCmd = data.get('bmsOnBdChrgTrgtSOCDspCmd')
        self.bms_estd_elec_rng = data.get('bmsEstdElecRng')
        self.bmsAltngChrgCrntDspCmd = data.get('bmsAltngChrgCrntDspCmd')
        self.bmsChrgCtrlDspCmd = data.get('bmsChrgCtrlDspCmd')
        self.chrgngRmnngTime = data.get('chrgngRmnngTime')
        self.chrgngRmnngTimeV = data.get('chrgngRmnngTimeV')
        self.bmsChrgOtptCrntReq = data.get('bmsChrgOtptCrntReq')
        self.bmsChrgOtptCrntReqV = data.get('bmsChrgOtptCrntReqV')
        self.bmsPackCrnt = data.get('bmsPackCrnt')
        self.bmsPackCrntV = data.get('bmsPackCrntV')
        self.bmsPackVol = data.get('bmsPackVol')
        self.bmsPackSOCDsp = data.get('bmsPackSOCDsp')
        self.bmsChrgSts = data.get('bmsChrgSts')
        self.bmsChrgSpRsn = data.get('bmsChrgSpRsn')
        self.clstrElecRngToEPT = data.get('clstrElecRngToEPT')
        self.bmsPTCHeatReqDspCmd = data.get('bmsPTCHeatReqDspCmd')
        self.bmsPTCHeatResp = data.get('bmsPTCHeatResp')
        self.ccuEleccLckCtrlDspCmd = data.get('ccuEleccLckCtrlDspCmd')
        self.bmsPTCHeatSpRsn = data.get('bmsPTCHeatSpRsn')
        self.bmsDsChrgSpRsn = data.get('bmsDsChrgSpRsn')
        self.disChrgngRmnngTime = data.get('disChrgngRmnngTime')
        self.disChrgngRmnngTimeV = data.get('disChrgngRmnngTimeV')
        self.imcuVehElecRng = data.get('imcuVehElecRng')
        self.imcuVehElecRngV = data.get('imcuVehElecRngV')
        self.imcuChrgngEstdElecRng = data.get('imcuChrgngEstdElecRng')
        self.imcuChrgngEstdElecRngV = data.get('imcuChrgngEstdElecRngV')
        self.imcuDschrgngEstdElecRng = data.get('imcuDschrgngEstdElecRng')
        self.imcuDschrgngEstdElecRngV = data.get('imcuDschrgngEstdElecRngV')
        self.chrgngSpdngTime = data.get('chrgngSpdngTime')
        self.chrgngSpdngTimeV = data.get('chrgngSpdngTimeV')
        self.chrgngAddedElecRng = data.get('chrgngAddedElecRng')
        self.chrgngAddedElecRngV = data.get('chrgngAddedElecRngV')
        self.onBdChrgrAltrCrntInptCrnt = data.get('onBdChrgrAltrCrntInptCrnt')
        self.onBdChrgrAltrCrntInptVol = data.get('onBdChrgrAltrCrntInptVol')
        self.ccuOnbdChrgrPlugOn = data.get('ccuOnbdChrgrPlugOn')
        self.ccuOffBdChrgrPlugOn = data.get('ccuOffBdChrgrPlugOn')
        self.chrgngDoorPosSts = data.get('chrgngDoorPosSts')
        self.chrgngDoorOpenCnd = data.get('chrgngDoorOpenCnd')
        self.chargeStatus = RvsChargingStatus()
        self.chargeStatus.init_from_dict(data.get('chargeStatus'))
        self.bmsAdpPubChrgSttnDspCmd = data.get('bmsAdpPubChrgSttnDspCmd')

    def get_current(self) -> float:
        return self.bmsPackCrnt * 0.05 - 1000.0

    def get_voltage(self) -> float:
        return self.bmsPackVol * 0.25

    def get_power(self) -> float:
        return self.get_current() * self.get_voltage() / 1000.0

    def get_charge_target_soc(self) -> TargetBatteryCode | None:
        raw_target_soc = self.bmsOnBdChrgTrgtSOCDspCmd
        try:
            return TargetBatteryCode(raw_target_soc)
        except ValueError:
            return None


class RvsChargingStatus(Asn1Type):
    def __init__(self):
        super().__init__('RvsChargingStatus')
        self.real_time_power: int | None = None  # INTEGER(0..65535),
        self.charging_gun_state: bool | None = None  # BOOLEAN,
        self.fuel_Range_elec: int | None = None  # INTEGER(0..65535),
        self.charging_type: int | None = None  # INTEGER(0..255),
        self.start_time: int | None = None  # INTEGER(0..2147483647) OPTIONAL,
        self.end_time: int | None = None  # INTEGER(0..2147483647) OPTIONAL,
        self.charging_pile_id: str | None = None  # IA5String(SIZE(0..64)) OPTIONAL,
        self.charging_pile_supplier: str | None = None  # IA5String(SIZE(0..64)) OPTIONAL,
        self.working_current: int | None = None  # INTEGER(0..65535) OPTIONAL,
        self.working_voltage: int | None = None  # INTEGER(0..65535) OPTIONAL,
        self.mileage_since_last_charge: int | None = None  # INTEGER(0..65535) OPTIONAL,
        self.power_usage_since_last_charge: int | None = None  # INTEGER(0..65535) OPTIONAL,
        self.mileage_of_day: int | None = None  # INTEGER(0..65535) OPTIONAL,
        self.power_usage_of_day: int | None = None  # INTEGER(0..65535) OPTIONAL,
        self.static_energy_consumption: int | None = None  # INTEGER(0..65535) OPTIONAL,
        self.charging_electricity_phase: int | None = None  # INTEGER(0..255) OPTIONAL,
        self.charging_duration: int | None = None  # INTEGER(0..2147483647) OPTIONAL,
        self.last_charge_ending_power: int | None = None  # INTEGER(0..65535) OPTIONAL,
        self.total_battery_capacity: int | None = None  # INTEGER(0..65535) OPTIONAL,
        self.fota_lowest_voltage: int | None = None  # INTEGER(0..255) OPTIONAL,
        self.mileage: int | None = None  # INTEGER(0..2147483647),
        self.extended_data1: int | None = None  # INTEGER(0..2147483647) OPTIONAL,
        self.extended_data2: int | None = None  # INTEGER(0..2147483647) OPTIONAL,
        self.extended_data3: str | None = None  # IA5String(SIZE(0..1024)) OPTIONAL,
        self.extended_data4: str | None = None  # IA5String(SIZE(0..1024)) OPTIONAL

    def get_data(self) -> dict:
        data = {
            'realtimePower': self.real_time_power,
            'chargingGunState': self.charging_gun_state,
            'fuelRangeElec': self.fuel_Range_elec,
            'chargingType': self.charging_type,
            'mileage': self.mileage
        }
        self.add_optional_field_to_data(data, 'startTime', self.start_time)
        self.add_optional_field_to_data(data, 'endTime', self.end_time)
        self.add_optional_field_to_data(data, 'chargingPileID', self.charging_pile_id)
        self.add_optional_field_to_data(data, 'chargingPileSupplier', self.charging_pile_supplier)
        self.add_optional_field_to_data(data, 'workingCurrent', self.working_current)
        self.add_optional_field_to_data(data, 'workingVoltage', self.working_voltage)
        self.add_optional_field_to_data(data, 'mileageSinceLastCharge', self.mileage_since_last_charge)
        self.add_optional_field_to_data(data, 'powerUsageSinceLastCharge', self.power_usage_since_last_charge)
        self.add_optional_field_to_data(data, 'mileageOfDay', self.mileage_of_day)
        self.add_optional_field_to_data(data, 'powerUsageOfDay', self.power_usage_of_day)
        self.add_optional_field_to_data(data, 'staticEnergyConsumption', self.static_energy_consumption)
        self.add_optional_field_to_data(data, 'chargingElectricityPhase', self.charging_electricity_phase)
        self.add_optional_field_to_data(data, 'chargingDuration', self.charging_duration)
        self.add_optional_field_to_data(data, 'lastChargeEndingPower', self.last_charge_ending_power)
        self.add_optional_field_to_data(data, 'totalBatteryCapacity', self.total_battery_capacity)
        self.add_optional_field_to_data(data, 'fotaLowestVoltage', self.fota_lowest_voltage)
        self.add_optional_field_to_data(data, 'extendedData1', self.extended_data1)
        self.add_optional_field_to_data(data, 'extendedData2', self.extended_data2)
        self.add_optional_field_to_data(data, 'extendedData3', self.extended_data3)
        self.add_optional_field_to_data(data, 'extendedData4', self.extended_data4)
        return data

    def init_from_dict(self, data: dict) -> None:
        self.real_time_power = data.get('realtimePower')
        self.charging_gun_state = data.get('chargingGunState')
        self.fuel_Range_elec = data.get('fuelRangeElec')
        self.charging_type = data.get('chargingType')
        self.start_time = data.get('startTime')
        self.end_time = data.get('endTime')
        self.charging_pile_id = data.get('chargingPileID')
        self.charging_pile_supplier = data.get('chargingPileSupplier')
        self.working_current = data.get('workingCurrent')
        self.working_voltage = data.get('workingVoltage')
        self.mileage_since_last_charge = data.get('mileageSinceLastCharge')
        self.power_usage_since_last_charge = data.get('powerUsageSinceLastCharge')
        self.mileage_of_day = data.get('mileageOfDay')
        self.power_usage_of_day = data.get('powerUsageOfDay')
        self.static_energy_consumption = data.get('staticEnergyConsumption')
        self.charging_electricity_phase = data.get('chargingElectricityPhase')
        self.charging_duration = data.get('chargingDuration')
        self.last_charge_ending_power = data.get('lastChargeEndingPower')
        self.total_battery_capacity = data.get('totalBatteryCapacity')
        self.fota_lowest_voltage = data.get('fotaLowestVoltage')
        self.mileage = data.get('mileage')
        self.extended_data1 = data.get('extendedData1')
        self.extended_data2 = data.get('extendedData2')
        self.extended_data3 = data.get('extendedData3')
        self.extended_data4 = data.get('extendedData4')


class OtaChrgCtrlReq(ApplicationData):
    def __init__(self):
        super().__init__('OTAChrgCtrlReq')
        self.chrgCtrlReq: int | None = None
        self.tboxV2XReq: int | None = None
        self.tboxEleccLckCtrlReq: int | None = None

    def get_data(self) -> dict:
        data = {
            'chrgCtrlReq': self.chrgCtrlReq,
            'tboxV2XReq': self.tboxV2XReq,
            'tboxEleccLckCtrlReq': self.tboxEleccLckCtrlReq,
        }
        return data

    def init_from_dict(self, data: dict):
        self.chrgCtrlReq = data.get('chrgCtrlReq')
        self.tboxV2XReq = data.get('tboxV2XReq')
        self.tboxEleccLckCtrlReq = data.get('tboxEleccLckCtrlReq')


class OtaChrgCtrlStsResp(ApplicationData):
    def __init__(self):
        super().__init__('OTAChrgCtrlStsResp')
        self.chrgCtrlDspCmd: int | None = None  # INTEGER(0..255)
        self.chrgCtrlResp: int | None = None  # INTEGER(0..255)
        self.bmsDsChrgCtrlDspCmd: int | None = None  # INTEGER(0..255) OPTIONAL
        self.bmsDsChrgCtrlResp: int | None = None  # INTEGER(0..255) OPTIONAL
        self.ccuEleccLckCtrlDspCmd: int | None = None  # INTEGER(0..255) OPTIONAL
        self.ccuEleccLckCtrlResp: int | None = None  # INTEGER(0..255) OPTIONAL
        self.rvcReqSts: str | None = None  # OCTET STRING(SIZE(1)) OPTIONAL

    def get_data(self) -> dict:
        data = {
            'chrgCtrlDspCmd': self.chrgCtrlDspCmd,
            'chrgCtrlResp': self.chrgCtrlResp,
        }
        self.add_optional_field_to_data(data, 'bmsDsChrgCtrlDspCmd', self.bmsDsChrgCtrlDspCmd)
        self.add_optional_field_to_data(data, 'bmsDsChrgCtrlResp', self.bmsDsChrgCtrlResp)
        self.add_optional_field_to_data(data, 'ccuEleccLckCtrlDspCmd', self.ccuEleccLckCtrlDspCmd)
        self.add_optional_field_to_data(data, 'ccuEleccLckCtrlResp', self.ccuEleccLckCtrlResp)
        self.add_optional_field_to_data(data, 'rvcReqSts', self.rvcReqSts)
        return data

    def init_from_dict(self, data: dict):
        self.chrgCtrlDspCmd = data.get('chrgCtrlDspCmd')
        self.chrgCtrlResp = data.get('chrgCtrlResp')
        self.bmsDsChrgCtrlDspCmd = data.get('bmsDsChrgCtrlDspCmd')
        self.bmsDsChrgCtrlResp = data.get('bmsDsChrgCtrlResp')
        self.ccuEleccLckCtrlDspCmd = data.get('ccuEleccLckCtrlDspCmd')
        self.ccuEleccLckCtrlResp = data.get('ccuEleccLckCtrlResp')
        if 'rvcReqSts' in data:
            self.rvcReqSts = data.get('rvcReqSts').decode()


class OtaChrgRsvanReq(ApplicationData):
    def __init__(self):
        super().__init__('OTAChrgRsvanReq')
        self.rsvanStHour: int | None = None  # INTEGER(0..255)
        self.rsvanStMintu: int | None = None  # INTEGER(0..255)
        self.rsvanSpHour: int | None = None  # INTEGER(0..255)
        self.rsvanSpMintu: int | None = None  # INTEGER(0..255)
        self.tboxReserCtrlReq: int | None = None  # INTEGER(0..255)
        self.tboxAdpPubChrgSttnReq: int | None = None  # INTEGER(0..255)

    def get_data(self) -> dict:
        data = {
            'rsvanStHour': self.rsvanStHour,
            'rsvanStMintu': self.rsvanStMintu,
            'rsvanSpHour': self.rsvanSpHour,
            'rsvanSpMintu': self.rsvanSpMintu,
            'tboxReserCtrlReq': self.tboxReserCtrlReq,
            'tboxAdpPubChrgSttnReq': self.tboxAdpPubChrgSttnReq
        }
        return data

    def init_from_dict(self, data: dict):
        self.rsvanStHour = data.get('rsvanStHour')
        self.rsvanStMintu = data.get('rsvanStMintu')
        self.rsvanSpHour = data.get('rsvanSpHour')
        self.rsvanSpMintu = data.get('rsvanSpMintu')
        self.tboxReserCtrlReq = data.get('tboxReserCtrlReq')
        self.tboxAdpPubChrgSttnReq = data.get('tboxAdpPubChrgSttnReq')


class OtaChrgRsvanResp(ApplicationData):
    def __init__(self):
        super().__init__('OTAChrgRsvanResp')
        self.rvcReqSts: bytes | None = None  # OCTET STRING(SIZE(1))
        self.bmsReserCtrlDspCmd: int | None = None  # INTEGER(0..255)
        self.bmsReserStHourDspCmd: int | None = None  # INTEGER(0..255)
        self.bmsReserStMintueDspCmd: int | None = None  # INTEGER(0..255)
        self.bmsReserSpHourDspCmd: int | None = None  # INTEGER(0..255)
        self.bmsReserSpMintueDspCmd: int | None = None  # INTEGER(0..255)
        self.bmsAdpPubChrgSttnDspCmd: int | None = None  # INTEGER(0..255)
        self.bmsReserChrCtrlResp: int | None = None  # INTEGER(0..255) OPTIONAL

    def get_data(self) -> dict:
        data = {
            'rvcReqSts': self.rvcReqSts.decode(),
            'bmsReserCtrlDspCmd': self.bmsReserCtrlDspCmd,
            'bmsReserStHourDspCmd': self.bmsReserStHourDspCmd,
            'bmsReserStMintueDspCmd': self.bmsReserStMintueDspCmd,
            'bmsReserSpHourDspCmd': self.bmsReserSpHourDspCmd,
            'bmsReserSpMintueDspCmd': self.bmsReserSpMintueDspCmd,
            'bmsAdpPubChrgSttnDspCmd': self.bmsAdpPubChrgSttnDspCmd,
        }
        self.add_optional_field_to_data(data, 'bmsReserChrCtrlResp', self.bmsReserChrCtrlResp)
        return data

    def init_from_dict(self, data: dict):
        self.rvcReqSts = data.get('rvcReqSts')
        self.bmsReserCtrlDspCmd = data.get('bmsReserCtrlDspCmd')
        self.bmsReserStHourDspCmd = data.get('bmsReserStHourDspCmd')
        self.bmsReserStMintueDspCmd = data.get('bmsReserStMintueDspCmd')
        self.bmsReserSpHourDspCmd = data.get('bmsReserSpHourDspCmd')
        self.bmsReserSpMintueDspCmd = data.get('bmsReserSpMintueDspCmd')
        self.bmsAdpPubChrgSttnDspCmd = data.get('bmsAdpPubChrgSttnDspCmd')
        self.bmsReserChrCtrlResp = data.get('bmsReserChrCtrlResp')


class OtaChrgSetngReq(ApplicationData):
    def __init__(self):
        super().__init__('OTAChrgSetngReq')
        self.onBdChrgTrgtSOCReq: int | None = None  # INTEGER(0..255)
        self.altngChrgCrntReq: int | None = None  # INTEGER(0..255)
        self.tboxV2XSpSOCReq: int | None = None  # INTEGER(0..255)

    def get_data(self) -> dict:
        data = {
            'onBdChrgTrgtSOCReq': self.onBdChrgTrgtSOCReq,
            'altngChrgCrntReq': self.altngChrgCrntReq,
            'tboxV2XSpSOCReq': self.tboxV2XSpSOCReq
        }
        return data

    def init_from_dict(self, data: dict):
        self.onBdChrgTrgtSOCReq = data.get('onBdChrgTrgtSOCReq')
        self.altngChrgCrntReq = data.get('altngChrgCrntReq')
        self.tboxV2XSpSOCReq = data.get('tboxV2XSpSOCReq')


class OtaChrgSetngResp(ApplicationData):
    def __init__(self):
        super().__init__('OTAChrgSetngResp')
        self.rvcReqSts: bytes | None = None  # OCTET STRING(SIZE(1))
        self.bmsOnBdChrgTrgtSOCDspCmd: int | None = None  # INTEGER(0..255)
        self.bmsChrgTrgtSOCResp: int | None = None  # INTEGER(0..255)
        self.bmsEstdElecRng: int | None = None  # INTEGER(0..65535)
        self.bmsAltngChrgCrntDspCmd: int | None = None  # INTEGER(0..255)
        self.bmsPackCrnt: int | None = None  # INTEGER(0..65535)
        self.bmsAltngChrgCrntResp: int | None = None  # INTEGER(0..255)
        self.imcuDschrgTrgtSOCDspCmd: int | None = None  # INTEGER(0..255) OPTIONAL
        self.imcuDschrgTrgtSOCResp: int | None = None  # INTEGER(0..255) OPTIONAL

    def get_data(self) -> dict:
        data = {
            'rvcReqSts': self.rvcReqSts.decode(),
            'bmsOnBdChrgTrgtSOCDspCmd': self.bmsOnBdChrgTrgtSOCDspCmd,
            'bmsChrgTrgtSOCResp': self.bmsChrgTrgtSOCResp,
            'bmsEstdElecRng': self.bmsEstdElecRng,
            'bmsAltngChrgCrntDspCmd': self.bmsAltngChrgCrntDspCmd,
            'bmsPackCrnt': self.bmsPackCrnt,
            'bmsAltngChrgCrntResp': self.bmsAltngChrgCrntResp
        }
        self.add_optional_field_to_data(data, 'imcuDschrgTrgtSOCDspCmd', self.imcuDschrgTrgtSOCDspCmd)
        self.add_optional_field_to_data(data, 'imcuDschrgTrgtSOCResp', self.imcuDschrgTrgtSOCResp)
        return data

    def init_from_dict(self, data: dict):
        self.rvcReqSts = data.get('rvcReqSts')
        self.bmsOnBdChrgTrgtSOCDspCmd = data.get('bmsOnBdChrgTrgtSOCDspCmd')
        self.bmsChrgTrgtSOCResp = data.get('bmsChrgTrgtSOCResp')
        self.bmsEstdElecRng = data.get('bmsEstdElecRng')
        self.bmsAltngChrgCrntDspCmd = data.get('bmsAltngChrgCrntDspCmd')
        self.bmsPackCrnt = data.get('bmsPackCrnt')
        self.bmsAltngChrgCrntResp = data.get('bmsAltngChrgCrntResp')
        self.imcuDschrgTrgtSOCDspCmd = data.get('imcuDschrgTrgtSOCDspCmd')
        self.imcuDschrgTrgtSOCResp = data.get('imcuDschrgTrgtSOCResp')


class OtaChrgHeatReq(ApplicationData):
    def __init__(self):
        super().__init__('OTAChrgHeatReq')
        self.ptcHeatReq: int | None = None  # INTEGER(0..255)

    def get_data(self) -> dict:
        data = {
            'ptcHeatReq': self.ptcHeatReq
        }
        return data

    def init_from_dict(self, data: dict):
        self.ptcHeatReq = data.get('ptcHeatReq')


class OtaChrgHeatResp(ApplicationData):
    def __init__(self):
        super().__init__('OTAChrgHeatResp')
        self.ptcHeatReqDspCmd: int | None = None  # INTEGER(0..255)
        self.ptcHeatResp: int | None = None  # INTEGER(0..255)
        self.rvcReqSts: bytes | None = None  # OCTET STRING(SIZE(1))

    def get_data(self) -> dict:
        data = {
            'ptcHeatReqDspCmd': self.ptcHeatReqDspCmd,
            'ptcHeatResp': self.ptcHeatResp,
            'rvcReqSts': self.rvcReqSts.decode()
        }
        return data

    def init_from_dict(self, data: dict):
        self.ptcHeatReqDspCmd = data.get('ptcHeatReqDspCmd')
        self.ptcHeatResp = data.get('ptcHeatResp')
        self.rvcReqSts = data.get('rvcReqSts')
