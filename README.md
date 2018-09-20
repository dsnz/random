# random

this repository contains very good performing and simple (basic) random number generators

**philox** is a pure python implementation of the Philox counter algorithm which runs just ~ 2.5 times slower than the native python random number generator
 
see [Counter-based random number generator (CBRNG) on Wikipedia](https://en.wikipedia.org/wiki/Counter-based_random_number_generator_(CBRNG))

## How to use

import philox

philox.random()

[optionally call first philox.seed(\<seed\>)]


## License

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
