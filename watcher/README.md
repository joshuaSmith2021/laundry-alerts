# watcher
The role of the watcher is to check the prometheus export for the current state of residence halls and machines. It then compares the current state of each machine to its past state in the redis database. If a change has occured, for example a type of machine is now available in a residence hall, it queues an alert to the alerts list.
