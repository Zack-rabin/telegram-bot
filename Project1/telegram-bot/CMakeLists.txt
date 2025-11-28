cmake_minimum_required(VERSION 3.10)
project(my-telegram-bot)
set(CMAKE_CXX_STANDARD 17)

# Enable vcpkg integration
set(CMAKE_TOOLCHAIN_FILE "C:/vcpkg/scripts/buildsystems/vcpkg.cmake")

# Find tgbot-cpp library

find_package(tgbot-cpp CONFIG REQUIRED)

# Add the executable
add_executable(mybot main.cpp)
target_link_libraries(mybot PRIVATE tgbot-cpp::tgbot-cpp)




