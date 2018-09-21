---
title: "Metwork presentation"
date: 2018-02-07T14:06:34+01:00
weight: 10
---
Metwork is a set of various modules that allow you to perform very diverse tasks like data pre-processing, data storage or management of buses. These modules were designed to work together so there will not be any compatibility problem between each of them.

These modules originate from a project designed to store large amount of data refreshed regularly and handle numerous user querries on this data. A user would make a querry that would be load balanced, then put into a bus until the querried data is returned. Meanwhile, raw data would be pushed regularly to the server. This raw data would be pre-processed then stored. Because the data depended on time and was perishable, the system was supposed to know which data was the latest and to dispose of deprecated data.

Metwork regroups these modules, but make them usable on a wider scale by generalizing them and removing the business part and only keeping the software architecture. Not only do these modules work well on their own, but they also synergize very well with each other.
