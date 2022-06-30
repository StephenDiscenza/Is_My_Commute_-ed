# How Bad is My Commute?
#### Video Demo:  <URL HERE>
#### Description:
Travel durations, especially durring rush hour, on the NYC subway are often far longer than suggested by Google and other services. The aim of this project it to combine realtime data with historical data to give a more accurate prediction of travel times.

The real time data is from a series of APIs maintained by the MTA. The data is in gtfs-rt (General Transit Feed Specification Realtime) format. The information we as travelers get concerning 

## Set Up
There is some quirkyness with the required packages. In particular the most recent version of protobuf, included when installing gtfs-realtime-bindings is broken. As a workaround, you can uninstall protobuf and reinstall it with:
    pip install protobuf==3.20.1
    