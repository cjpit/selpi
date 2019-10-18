# Selpi

Selpi is woefully incomplete, but in the long run it will hopefully be a collection of basic utilties to monitor a Selectronic SP Pro 2 from a RaspberryPi.

Additional docs:

 * [Connecting](docs/connecting.md)
 * [Protocol](docs/protocol.md)

# pvo-sppro2.py

The Python script `pvo-sppro2.py` is designed to upload basic data from a SP Pro 2 to [pvoutput.org](https://pvoutput.org/).

Once [connected](docs/connecting.md) to a SP Pro, modify the script to include your PVO credentials and the appropriate `ttyUSB` device. Run it with `python pvo-sppro2.py`.