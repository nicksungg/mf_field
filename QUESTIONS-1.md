* embed PDE in input? embed solver?
* benchmark u-net on high freq?
* first train on HF -> then train on LF -> then train on HF?
* from HF, understand what LF would look like (since LF might shift over), then train to predict HF
* feed HF and LF at the same time?
* best models tend to produce blurry results since it's the average of sharp results
* LF might have warping compared to HF (shouldn't do pixel to pixel correlation in this case)

