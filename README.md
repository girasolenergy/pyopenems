# pyopenems

    $ pip install pyopenems

## cli

    $ python -m openems --server-url='ws://localhost:8081' --username='admin' --password='password' get-edge-list
    edge0
    edge1
    edge3
    edge4
    edge5
    edge6

    $ python -m openems --server-url='ws://localhost:8081' --username='admin' --password='password' get-edge-config edge0
    {
      "components": {
        "_appManager": {
          "alias": "Core.AppManager",
          "factoryId": "Core.AppManager",
          "properties": {
            "apps": "[]",
            "keyForFreeApps": "0000-0000-0000-0000"
          },
          "channels": {

### fetching meter value

    $ python -m openems ... get-meter-list edge0
    meter0
    meter1

    $ python -m openems ... get-channel-list edge0 meter0 | head
    meter0/ActiveConsumptionEnergy
    meter0/ActiveConsumptionEnergyL1
    meter0/ActiveConsumptionEnergyL2
    meter0/ActiveConsumptionEnergyL3
    meter0/ActivePower
    meter0/ActivePowerL1
    meter0/ActivePowerL2
    meter0/ActivePowerL3
    meter0/ActiveProductionEnergy
    meter0/ActiveProductionEnergyDaily

    $ python -m openems ... get-channel-data edge0 meter0/ActiveConsumptionEnergy 2024-01-01 2024-01-01
    ,meter0/ActiveConsumptionEnergy
    2023-12-31T15:00:00Z,5831900.0
    2023-12-31T15:05:00Z,5831900.0
    2023-12-31T15:10:00Z,5831900.0
    2023-12-31T15:15:00Z,5832000.0
    2023-12-31T15:20:00Z,5832000.0
    (snip)
    2024-01-01T14:35:00Z,5837900.0
    2024-01-01T14:40:00Z,5838000.0
    2024-01-01T14:45:00Z,5838000.0
    2024-01-01T14:50:00Z,5838000.0
    2024-01-01T14:55:00Z,5838100.0

### fetching pvinverter value

    $ python -m openems ... get-pvinverter-list edge0
    pvInverter1

    $ python -m openems ... get-channel-list edge0 pvInverter1 | head
    pvInverter1/ActiveConsumptionEnergy
    pvInverter1/ActiveConsumptionEnergyL1
    pvInverter1/ActiveConsumptionEnergyL2
    pvInverter1/ActiveConsumptionEnergyL3
    pvInverter1/ActivePower
    pvInverter1/ActivePowerL1
    pvInverter1/ActivePowerL2
    pvInverter1/ActivePowerL3
    pvInverter1/ActivePowerLimit
    pvInverter1/ActiveProductionEnergy

    $ python -m openems ... get-channel-data edge0 pvInverter0/ActiveProductionEnergy 2024-01-01 2024-01-01
    2023-12-31 15:00:00+00:00,5700.0
    2023-12-31 15:05:00+00:00,5700.0
    2023-12-31 15:10:00+00:00,5700.0
    2023-12-31 15:15:00+00:00,5700.0
    2023-12-31 15:20:00+00:00,5700.0
    2023-12-31 15:25:00+00:00,5700.0
    2023-12-31 15:30:00+00:00,5700.0
    2023-12-31 15:35:00+00:00,5700.0
    2023-12-31 15:40:00+00:00,5700.0


### setting controller value

    $ python -m openems update-component-config edge0 ctrlPeakShaving0 peakShavingPower 300
