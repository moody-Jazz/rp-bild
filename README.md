# Rp-bild

This is a lightweight custom Python build system to manage compilation, linking, cleaning, and initializing C/C++ projects that use [Raylib](https://github.com/raysan5/raylib). It's designed to be simple, automatic, and cross-platform.

## Project Structure After Initialization

```
your_project/
├── rpbild.py
├── include/
│   └── raylib.h
├── lib/
│   └── libraylib.a
├── obj/
│   └── *.o (object files)
├── src/
│   └── main.c / main.cpp
```
Put all your headers into include/ and all your .c/.cpp files in src
## Usage
to get started, simply create or navigate to your project folder, copy `rpbild.py` into it, then run `python rpbild.py init` to set up your project and Raylib dependency—once initialized, you're ready to build, clean, and expand your project from there.
```bash
python rpbild.py [command]
```

### Available Commands

#### init

Initializes a new Raylib project:
- Prompts for language (`c` or `cpp`)
- Clones Raylib into the root folder
- Builds Raylib as a static library
- Copies:
  - `raylib.h` → `include/`
  - `libraylib.a` → `lib/`
- Creates `src/` and places an example file as `main.c` or `main.cpp`

```bash
python rpbild.py init
```

#### compile *(default)*

- Checks all source files in `src/`
- Recompiles if:
  - The `.o` file is missing
  - The source file has been modified more recently than its object file
- Links all `.o` files into a final executable (`main`)

Or simply:

```bash
python rpbild.py
```

This defaults to `compile`.

```bash
python rpbild.py compile
```
#### clean

Deletes all generated object files and the `obj/` directory.

```bash
python rpbild.py clean
```




## Requirements

- Python 3.x
- `git`
- make
- A C/C++ compiler (clang or gcc)
