#include <iostream>
#include <string>
#include <curl/curl.h>


static size_t WriteCallback(void *contents, size_t size, size_t nmemb, void *userp){
  std::cout << contents << std::endl;
  ((std::string*)userp)->append((char*)contents, size * nmemb);
  return size * nmemb;
}

int main(void){
  CURL *handle;
  CURLcode res;
  std::string readBuffer;

  handle = curl_easy_init();
  if(handle) {
    curl_easy_setopt(handle, CURLOPT_URL, "https://qrng.anu.edu.au/API/jsonI.php?length=1&type=uint16");
    curl_easy_setopt(handle, CURLOPT_WRITEFUNCTION, WriteCallback);
    curl_easy_setopt(handle, CURLOPT_WRITEDATA, &readBuffer);
    res = curl_easy_perform(handle);
    curl_easy_cleanup(handle);

    std::cout << readBuffer << std::endl;
  }
  return 0;
}