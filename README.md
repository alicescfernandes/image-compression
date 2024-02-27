# Image Compression

This project implements the building blocks of the JPEG compression algorithm. It uses the default quantification tables instead of calculating new ones, and applies the huffman encoding for the actual image compression

## Why?
While i was taking my engeneering degree, i had a course that was focused on this particular topic, however all the coursework i delivered was enough to pass the class but i didn't understood exactly how it worked. Since my day job is on a streaming product, and i work with playback, i wanted to understand how encoding worked. While this project only implements JPEG, and only the blocks (and not the format iself), it is a good learning project to understand where the image looses quality, and how JPEG optimizes the visual information.

Obviously, this project is working with static pictures, but a video is more like moving pictures, but video is just an extension of images, and H264 follows the same encoding process, but adds more optimizations on top to save even more video. There are alot of repos that also do the JPEG encoding / decoding in full, but i was more interested in knowing what each block does.

Currently this code only encodes the luma channel, but maybe one day i can get it to do the chroma channels aswell

There are alot of resources that out there, but my favourite is https://github.com/leandromoreira/digital_video_introduction, which touches on the topics that this project implements and its easy to read.
