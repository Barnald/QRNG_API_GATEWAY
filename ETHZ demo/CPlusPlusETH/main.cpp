#include <iostream>
#include "remote_engine.hpp"

int main() {
    openqu::random::remote_engine rng("http://qrng.ethz.ch/api/randint");
    std::cout << "Random number: " << rng() << std::endl;
}
