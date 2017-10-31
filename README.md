# Similarity Annotation Tool

A web based tool to annotate similarity of sounds regarding a target sound. 
The web application is written in django framework and the interface for annotation is based on [CrowdCurio audio annotator](https://github.com/CrowdCurio/audio-annotator) 

## Installation
First of all you should clone this repository
### 1. Install ffmpeg

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

### 2. Setup DB
#### 2.1 Installation
We recommend using postgreSQL database.

On Linux:
```
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
```

On Mac using HomeBrew follow [this](https://chartio.com/resources/tutorials/how-to-start-postgresql-server-on-mac-os-x/)

#### 2.2 Create DB
```
createdb _data_base_name_
```

### 3. Install requirements
We recommend using [virtualenv](https://virtualenv.pypa.io/en/stable/).
Once on your python virtual environment run:
```
pip install -r requirements.txt
```

### 4. Setup development settings
Copy the file simannotator/development_settings.py.dist to the same directory but with the file extension .py
Add your _data_base_name_ into DATABASES['NAME'] and the user of the database into DATABASES['USER']

### 5. Run the project
#### 5.1 Migrate
To apply the Django migrations to the DB run:
```
python manage.py migrate
```
#### 5.2 Run Django
```
python manage.py runserver
```

## License
All the software is distributed with the [Affero GPL v3 license](http://www.gnu.org/licenses/agpl-3.0.en.html) except the CrowdCurio files that are
licensed under BSD-2 clause.


