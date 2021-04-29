## What is it?

This is the **M**etwork **F**ramework **DATA** processing **module**. This module is a "production ready" framework
for processing "incoming files".

*Incoming files* can arrive by:

- system FTP
- system SCP
- Restful HTTP
- MQTT
- AMQP
- [...] (you can provide a "listener plugin" to support other things)

These "incoming files" are transient. The goal in to do something with them
**in the stream**.

To do that, you can easily code and provide **plugins** to build a
workflow. This workflow can be really easy and stupid (for example: do something
for every incoming files) but also really complex with hundreds of plugins, routing rules,
plugin sequences, file duplications...

To help with complex workflows, you can rely on :

- "loose coupling" and "dynamic business routing rules" between plugins thanks to the provided **switch plugin**
- "context transmission" thanks to the **xattrfile** library
- "full inspection support" in case of errors thanks to **failure policy**, **xattrfile** libraries and **archive plugins**
- "retry mechanisms" thanks to **failure policy** and **reinject plugins**
- "full monitoring" thanks to embedded metrics and logs management (and **mfadmin module**)

It's designed to process terrabytes of data every day in a very robust way:

- you can choose the parallelism level of each plugin with a configuration file
- plugins are automatically restarted if necessary
- "waiting queues" and "resources limits" protect the system for overloading

Last but not least, thanks to the "no polling at all" principle, you can process
several thousands of file by second.

## What is not in?

Of course, you can code the behavior you want but **mfdata module** is
mainly designed to be "stateless". If you want to store durably something,
have a look at **mfbase module**.
