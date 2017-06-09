# Smart House

## Abstract
Population aging is currently having a significant impact on health care systems.

Improvements in medical care are resulting in increased survival into old age, thus cognitive impairments and problems associated with aging will increase.
It has been estimated that one billion people will be over the age of 60 by the year 2025. 
As the burden of health-care in society increases, the need for finding more effective ways of providing care and support to the disabled and elderly at home becomes more predominant.

Automatic health monitoring systems are considered a key technology in this challenge, because they can serve a dual role:
  * to increase the safety and the sense of security of people living on their own
  * to allow elderly patients to be self-reliant longer, fostering their autonomy.
  
To this purpose, a smart controller called _MOTHER_ has  been introduced to collect data coming from sensors placed in several locations of the smart house.

## Sensor data

Five different sensor have been adopted to have a complete monitoring system that is able to communicate with a central unit _MOTHER_.
Several activities have been monitored: _Leaving_, _Toileting_, _Showering_, _Sleeping_, _Breakfast_, _Dinner_, _Drink_, _Idle/Unlabeled_, _Lunch_, _Snack_, _Spare time/TV_, _Grooming_.

Sensor data streams were divided in time slices of constant length.
For these experiments, sensor data were segmented in intervals of length ``Delta_t = 60 seconds``. 

At each time stamp, the following data are available:

```
Start time              End time                Activity	
--------------------    --------------------    --------
2012-11-11 21:14:00     2012-11-12 00:22:59     Spare_Time/TV
2012-11-12 00:24:00     2012-11-12 00:43:59     Spare_Time/TV
2012-11-12 00:48:00     2012-11-12 00:49:59     Grooming
```
```
Start time              End time                Location    Type        Place
--------------------    --------------------    --------    --------    --------
2012-11-11 21:14:21     2012-11-12 00:21:49     Seat        Pressure    Living
2012-11-12 00:22:57     2012-11-12 00:22:59     Door        PIR         Living
2012-11-12 00:23:14     2012-11-12 00:23:17     Door        PIR         Kitchen
```

## Goals

1. Data structure definition
    1. Sensor data measurements with their correlate timestamps
    2. Activities
  
2. Hidden Markov Model
    1. HMM structure definition in order to infer activities given sensor data
    2. Parameters estimation
    
3. Activity prevision
    1. Infer the user activities given sensors data

4. Data analysis
    1. Estimate model predictive capability comparing with ground truth
