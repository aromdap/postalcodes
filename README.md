## Installation

- Python based script `[python 3.8]` required to get started
- All dependencies can be found in `[requirements.txt]` file from Conda Environment used in local machine

### Clone

- Clone this repo to your local machine using `https://github.com/aromdap/postalcodes.git`

### Setup

- This script is ready to be run under Docker containers: you will get the outputs & logs in the current folder of your local machine

> Linux based: assuming Docker is already installed, build and run a self-removable container

```shell
$ sudo docker build --tag yourtag:1.0 .
$ sudo docker run --name yourname --rm -v "$(pwd)":/app yourtag:1.0
```

