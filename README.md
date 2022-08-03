# Master thesis
Repository to hold code and sources for my master thesis in Biomedical Computing.

Check [sources](sources/) for related papers.

The corresponding overleaf document can be found at https://www.overleaf.com/read/gzkkqcrkbntg (read only)

## Data acquisition
Simultaneous video and device data can be acquired by running the `video_recording.py` script.
Run the script with the device name as an argument on the command line like so:

```python video_recording.py Explore_XXXX```

Data is placed into a `data` folder, with device data recorded into CSV files and videos recorded as AVI files and placed into `data/videos`.
The script lets the user start video and device recordings simultaneously by entering a number key on the command line, to synchronize video start times, markers are set and recorded at the corresponding time stamp in the device CSV file and the video recording CSV file. A short delay between the markers is expected.

The recorded markers encode start and stop of a gesture / video in the last bit, the gesture type in the next 5 bits and the experiment number (currently unused) in the remaining bits. Check the documentation of `construct_marker` for details. Note that "^" in the documentation stands for exponentiation and not XOR.
