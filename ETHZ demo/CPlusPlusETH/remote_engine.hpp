// Copyright (C) 2015 Theoretical Physics, ETHZ Zurich

// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#pragma once

#include <curl/curl.h>

#include <vector>
#include <algorithm>
#include <string>
#include <limits>
#include <iostream>
#include <random>


#ifndef BYTE
// #define TEXT(x) Lx    //Unicode
// #define TCHAR wchar_t //Unicode
#define TCHAR char    //Not unicode
#define TEXT(x) x     //Not unicode
#define DWORD long
#define BYTE unsigned char
#endif


/** \addtogroup util
 *  @{
 */

/** @file remote_engine.hpp
 *
 *  This header defines the class @c remote_engine, which implement a remote random
 *  number engine conforming with the C++11 standards.
 */

namespace openqu {
namespace random {

namespace detail {
  static size_t WriteCallback(void *contents, size_t size, size_t nmemb, void *userp)
  {
      ((std::string*)userp)->append((char*)contents, size * nmemb);
      return size * nmemb;
  }
  
  
  const static TCHAR padCharacter = TEXT('=');
  std::vector<BYTE> base64Decode(const std::basic_string<TCHAR>& input)
  {
    if (input.length() % 4) //Sanity check
      throw std::runtime_error("Non-Valid base64!");
    size_t padding = 0;
    if (input.length())
    {
      if (input[input.length()-1] == padCharacter)
        padding++;
      if (input[input.length()-2] == padCharacter)
        padding++;
    }
    //Setup a vector to hold the result
    std::vector<BYTE> decodedBytes;
    decodedBytes.reserve(((input.length()/4)*3) - padding);
    DWORD temp=0; //Holds decoded quanta
    std::basic_string<TCHAR>::const_iterator cursor = input.begin();
    while (cursor < input.end())
    {
      for (size_t quantumPosition = 0; quantumPosition < 4; quantumPosition++)
      {
        temp <<= 6;
        if       (*cursor >= 0x41 && *cursor <= 0x5A) // This area will need tweaking if
          temp |= *cursor - 0x41;                  // you are using an alternate alphabet
        else if  (*cursor >= 0x61 && *cursor <= 0x7A)
          temp |= *cursor - 0x47;
        else if  (*cursor >= 0x30 && *cursor <= 0x39)
          temp |= *cursor + 0x04;
        else if  (*cursor == 0x2B)
          temp |= 0x3E; //change to 0x2D for URL alphabet
        else if  (*cursor == 0x2F)
          temp |= 0x3F; //change to 0x5F for URL alphabet
        else if  (*cursor == padCharacter) //pad
        {
          switch( input.end() - cursor )
          {
          case 1: //One pad character
            decodedBytes.push_back((temp >> 16) & 0x000000FF);
            decodedBytes.push_back((temp >> 8 ) & 0x000000FF);
            return decodedBytes;
          case 2: //Two pad characters
            decodedBytes.push_back((temp >> 10) & 0x000000FF);
            return decodedBytes;
          default:
            throw std::runtime_error("Invalid Padding in Base 64!");
          }
        }  else
          throw std::runtime_error("Non-Valid Character in Base 64!");
        cursor++;
      }
      decodedBytes.push_back((temp >> 16) & 0x000000FF);
      decodedBytes.push_back((temp >> 8 ) & 0x000000FF);
      decodedBytes.push_back((temp      ) & 0x000000FF);
    }
    return decodedBytes;
  }
  
  class curl_error : public std::runtime_error {
    public:
      curl_error(std::string const & msg)
      : std::runtime_error(msg)
      { }
  };
}





/**
 * @brief A remote random number engine
 *
 * The engine connects to an HTTP API to obtain random bytes as served
 * them as a standard C++11 random number engine.
 *
 */
class remote_engine {

public:
  typedef detail::curl_error curl_error;
  typedef std::uint64_t result_type;
  static const bool has_fixed_range = true;
  static const result_type min_value = std::numeric_limits<result_type>::min();
  static const result_type max_value = std::numeric_limits<result_type>::max();
  
  constexpr static result_type min()
  {
    return min_value;
  }

  constexpr static result_type max()
  {
    return max_value;
  }


 /** Constructor
  *  \param  url      full URL to the API endpoint, e.g. http://random.openqu.org/api
  *  \param  size     size of the buffer in units of `result_type`.
  */
  explicit remote_engine(std::string const & url, unsigned size=1024)
  : url_(url)
  , buf_(size, 0)
  , pos_(buf_.end())
  { }

 /** Generates a pseudo-random value. The state of the engine is advanced by one position.
  *  If the state reached the end of the buffer, a synchronous HTTP request is done to fill
  *  new numbers.
  *  \return a pseudo-random value.
  */
  result_type operator()()
  {
    if (pos_ == buf_.end() ) {
      fill_buffer();
      pos_ = buf_.begin();
    }
    return *(pos_++);
  }

   remote_engine(const remote_engine& ) =delete;
   void operator=(const remote_engine& ) =delete;
  
private:

  void fill_buffer()
  {
    try {
    CURL *curl;
    CURLcode res;
    std::string readBuffer;

    curl = curl_easy_init();
    if(curl) {
      std::size_t num_elements = buf_.size()*sizeof(result_type);
      std::string endpoint = url_+"/bytes?size="+std::to_string(num_elements);
      curl_easy_setopt(curl, CURLOPT_URL, endpoint.c_str());
      curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, detail::WriteCallback);
      curl_easy_setopt(curl, CURLOPT_WRITEDATA, &readBuffer);

      res = curl_easy_perform(curl);
      if (res != CURLE_OK)
        throw curl_error(curl_easy_strerror(res));
      
      long response_code;
      curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &response_code);
      if (response_code != 200)
        throw curl_error("Remote request failed with code: "+std::to_string(response_code)+"\n"+readBuffer);
      
      curl_easy_cleanup(curl);
    }
    
    
    // Decode data and copy to buffer
    std::vector<BYTE> data = detail::base64Decode(readBuffer);
    std::copy(data.begin(), data.end(), reinterpret_cast<BYTE *>(&buf_.front()));
    } catch (curl_error & e) {
      std::cerr << "WARNING: Problems with HTTP connection to the remote engine, falling back to a pseudo random number generator." << std::endl;
      std::cerr << "         CURL error was: " << e.what() << std::endl;
      
      // Seeding pseudo RNG from random_device
      using engine_type = std::mt19937_64;
      engine_type::result_type random_data[engine_type::state_size];
      std::random_device source;
      std::generate(std::begin(random_data), std::end(random_data), std::ref(source));
      std::seed_seq seeds(std::begin(random_data), std::end(random_data));
      engine_type engine(seeds);
      
      // Fill buffer
      std::generate(buf_.begin(), buf_.end(), std::ref(engine));
    }
  };
  
  std::string url_;
  std::vector<result_type> buf_;
  std::vector<result_type>::iterator pos_;

};

}
}
