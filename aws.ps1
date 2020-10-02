docker run --rm -it -v $env:USERPROFILE/.aws:/root/.aws -v "${PWD}:/aws" amazon/aws-cli $Args
