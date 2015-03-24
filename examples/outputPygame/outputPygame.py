#!/usr/bin/env python

'''
Decode the 5th first frame of the first video stream and write jpg (require pygame lib)

python outputPygame.py -m file.avi -> save frame 1 to 5
python outputPygame.py -m file.avi -o 140 -> save frame 140 to 145
'''

import sys
import ctypes
import copy

import pygame

from avpy import Media

if __name__ == '__main__':

    # cmdline
    from optparse import OptionParser

    usage = "usage: %prog -m foo.avi -o 140"
    parser = OptionParser(usage=usage)
    parser.add_option('-m', '--media', 
            help='play media')
    parser.add_option('-o', '--offset', 
            type='int',
            help='frame offset', default=0)
    parser.add_option('-c', '--frameCount', 
            type='int',
            help='number of image to save (default: %default)', default=5)
    parser.add_option('--copyPacket', 
            action='store_true',
            help='copy packet (debug only)')

    parser.add_option('--scaling', 
            default='bilinear',
            help='scaling algorithm')

    (options, args) = parser.parse_args()

    if not options.media:
        print('Please provide a media to play with -m or --media option')
        sys.exit(1)
    try:
        media = Media(options.media)
    except IOError as e:
        print('Unable to open %s: %s' % (options.media, e))
        sys.exit(1)

    # dump info
    mediaInfo = media.info()

    # select first video stream
    vstreams = [ i for i, s in enumerate(mediaInfo['stream']) if s['type'] == 'video' ]
    if vstreams:
        vstream = vstreams[0]
    else:
        print('No video stream in %s' % mediaInfo['name'])
        sys.exit(2)

    # retrieve video width and height
    streamInfo = mediaInfo['stream'][vstream]
    size = streamInfo['width'], streamInfo['height']

    print('video stream index: %d' % vstream)
    print('video stream resolution: %dx%d' % (size[0], size[1]))

    # pygame format require rgb24 (24 bits)
    media.addScaler(vstream, *size, scaling=options.scaling)

    decodedCount = 0
    # iterate over media
    for pkt in media:
        
        if pkt.streamIndex() == vstream:
            
            # copy packet if required - test only
            if options.copyPacket:
                pkt2 = copy.copy(pkt) 
            else:
                pkt2 = pkt

            pkt2.decode()
            if pkt2.decoded:

                decodedCount += 1
                print('decoded frame %d' % decodedCount)

                if decodedCount >= options.offset:
                    print('saving frame...')
                    
                    buf = pkt2.swsFrame.contents.data[0]
                    
                    # width*height*3 (rgb24)
                    bufLen = size[0]*size[1]*3
                    surfaceStr = ctypes.string_at(buf, bufLen)

                    surface = pygame.image.fromstring(surfaceStr, size, 'RGB')
                    pygame.image.save(surface, 'frame.%d.jpg' % decodedCount)
                
                if decodedCount >= options.offset + options.frameCount:
                    break 
