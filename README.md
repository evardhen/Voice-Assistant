# Voice-Assistant

This project is work in progress. 

To get it working, one needs to install the vosk models in the correct language (https://alphacephei.com/vosk/models) and install the requirements.txt.

The language is currently set to german, as are the logging comments. The language can be changed in the config.yml.

In the wakeword_detection() function in the main file, you have to select the correct microphone. You can identify it by commenting in the block and run the main. Afterwards, you have to adapt the microphone in the init of class VoiceAssistant().  

Currently, there are 4 intents implemented. A Wikipedia search, a time module, a reminder and and stop module.
