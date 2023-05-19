# mindbody_booker
Book courses in mindbody automatically. Following info are necessary:
* studio ID (set it in [credentials.py](./credentials.yaml))
* login credentials (set it in [credentials.py](./credentials.yaml))
* courses you want to book (see [example.yaml](./example.yaml))

REMARK: the setup used here is tested and used for only one studio. It might be possible that for other studio adaptions are necessary.  

Run the script with following command:
```
./mindbody_automate.py -c ./example.yaml
```

If the script should be executed headless (e.g. to run it on a raspberry pi without a screen), use the -hl flag.
