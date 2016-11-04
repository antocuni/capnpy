Scripts to run benchmarks on travis and then commit the results back to github

To create the travis RSA key:

1. ssh-keygen -t rsa -C "Travis CI key" -f ./travis/travis.rsa

2. travis encrypt-file ./travis/travis.rsa --add
