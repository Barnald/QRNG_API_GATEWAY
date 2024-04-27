#include <iostream>
#include "remote_engine.hpp"

int main() {
    openqu::random::remote_engine rng("http://random.openqu.org/api");
    std::cout << "Random number: " << rng() << std::endl;
}
