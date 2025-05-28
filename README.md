# Swift API Extractor

Extract a structured summary (including doc comments) of all classes, structs, protocols, enums, typealiases, variables, and functions from every `.swift` file in a directory.  
**Optimized for LLM (Large Language Model) understanding and codebase documentation.**

## Features

- Lists all types, protocols, enums, functions, and variables (with signatures)
- Includes documentation comments, inheritance, protocol conformances, and enum cases
- Outputs a readable summary for LLMs, onboarding, or documentation

## Requirements

- macOS (or Linux with Swift toolchain)
- [SourceKitten](https://github.com/jpsim/SourceKitten):  
  Install via Homebrew:
  ```sh
  brew install sourcekitten
  ```
- Python 3.7+

## Usage 
```sh
python swift_api_extractor.py -d /path/to/your/swift/project -o summary.txt
```

## Example Output
```plaintext
# File: ./Features/Auth/AuthRepository.swift

protocol AuthRepository
  Doc: Provides a layer between AuthService and the rest of the app, mapping errors and handling business logic...
  func signIn(email:password:)() -> Result<User, AuthError>
    Doc: Signs in a user with the given email and password.
...
```

## License
MIT
