#!/bin/bash
#
# Copyright 2016 Mario Ynocente Castro, Mathieu Bernard
#
# You can redistribute this file and/or modify it under the terms of
# the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

#
# Convert the jpeg files in a directory (and recursivly in
# subdirectories) into a mp4 video using avconv (one video per
# directory). This also create a m3u playlist of the generated videos
# in $data_dir
#

# make sure avconv is installed
[ -z $(which avconv 2> /dev/null) ] \
    && echo "Error: avconv not installed on your system." \
    && echo "Please run 'sudo apt-get install libav-tools'" \
    && exit 1

# remove any trailing slash and make it absolute
data_dir=$(readlink -f ${1%/})

# display a usage message if bad params
[ -z "$data_dir" ] && echo "Usage: $0 <directory>" && exit 0

# display error message if input is not a directory
[ ! -d "$data_dir" ] && echo "Error: $data_dir is not a directory"  && exit 1

# list all subdirectories containing at least one jpeg file
jpeg_dirs=$(find $data_dir -type f -name "*.jpeg" -exec dirname {} \; | uniq)

# display error message if no jpeg found
[ -z "$jpeg_dirs" ] && echo "Error: no jpeg file in $data_dir" && exit 1

rm -f $data_dir/playlist.m3u
for dir in $jpeg_dirs;
do
    # list all jpeg images in the directory
    jpeg=$(ls $dir/*.jpeg 2> /dev/null)

    # get the first jpeg file in the list
    first=$(echo $jpeg | cut -f1 -d' ')

    # find the length of the images index (just consider the first jpeg, we
    # assume they all have same index length)
    index=$(echo $first | sed -r 's|^.+_([0-9]+)\.jpeg$|\1|g')
    n=${#index}

    # jpeg files basename, with extension and index removed
    base=$(basename $first | sed -r 's|^(.+_)[0-9]+\.jpeg$|\1|g')

    # the global pattern matching jpeg files for avconv
    pattern=$(echo $dir/$base%0${n}d.jpeg)

    # convert the jpeg images into a video.avi
    avconv -y -framerate 24 -i $pattern -c:v libx264 -r 30 -pix_fmt yuv420p $dir/video.avi \
        || (echo "Error: failed to write video from $pattern"; exit 1)

    echo "Wrote $dir/video.avi"
    echo "$dir/video.avi" >> $data_dir/playlist.m3u
done

exit 0
