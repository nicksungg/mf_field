* We have a lot of LF data and not much HF data. the goal is to come up with a model that can predict HF well. i'm a human, so given an input, i need to learn to predict HF, but I just have abundant LF data. so what to do? To predict HF well, it might help if i know how HF converts to LF, so I can reverse the process and thus be able to convert LF to HF. It's like how if I want to learn to sharpen images, I could learn how to make them blurrier first and be able to reverse this. especially since LF could be the warped/distorted versions of HF. What if we have
* forward-NN predicts HF based off LF
* backward-NN predicts LF based of HF
* we use forward-NN to generate even more HF data, as a feedback loop. or run a GAN, discriminator between real/fake HF data
*
