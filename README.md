# Similarity Annotation Tool

A web based tool to annotate similarity of sounds regarding a target sound. 
The web application is written in django framework and the interface for annotation is based on [CrowdCurio audio annotator](https://github.com/CrowdCurio/audio-annotator) 

## Installation and run

### Getting ffmpeg set up

You may use **libav or ffmpeg**.

Mac (using [homebrew](http://brew.sh)):

```bash
# libav
brew install libav --with-libvorbis --with-sdl --with-theora

####    OR    #####

# ffmpeg
brew install ffmpeg --with-libvorbis --with-ffplay --with-theora
```

Linux (using aptitude):

```bash
# libav
apt-get install libav-tools libavcodec-extra-53

####    OR    #####

# ffmpeg
apt-get install ffmpeg libavcodec-extra-53
```

Windows:

1. Download and extract libav from [Windows binaries provided here](http://builds.libav.org/windows/).
2. Add the libav `/bin` folder to your PATH envvar
3. `pip install pydub`

Install [docker-compose](https://docs.docker.com/compose/install/) and then just run:

    docker-compose build
    docker-compose run

## License
All the software is distributed with the [Affero GPL v3 license](http://www.gnu.org/licenses/agpl-3.0.en.html) except the CrowdCurio files that are
licensed under BSD-2 clause.


