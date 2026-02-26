# Dracula Color Scheme - Complete Reference for Tilix

## Official Dracula Palette

### Primary Colors

```
Background:       #282936  ████████  Dark purple-gray
Foreground:       #F8F8F2  ████████  Off-white
Current Line:     #44475A  ████████  Medium gray-purple
Selection:        #44475A  ████████  Medium gray-purple
Comment:          #6272A4  ████████  Blue-gray
```

### ANSI Colors (Normal 0-7)

```
Black   (0):      #000000  ████████  Pure black
Red     (1):      #FF5454  ████████  Bright red
Green   (2):      #50FA7B  ████████  Bright green
Yellow  (3):      #F1FA8C  ████████  Bright yellow
Blue    (4):      #BD93F9  ████████  Purple
Magenta (5):      #FF79C6  ████████  Pink
Cyan    (6):      #8BE8FD  ████████  Cyan
White   (7):      #BFBFBF  ████████  Light gray
```

### ANSI Colors (Bright 8-15)

```
Bright Black   (8):   #4D4D4D  ████████  Dark gray
Bright Red     (9):   #FF6E67  ████████  Lighter red
Bright Green  (10):   #5AF78D  ████████  Lighter green
Bright Yellow (11):   #F4F99D  ████████  Lighter yellow
Bright Blue   (12):   #CAA8FA  ████████  Lighter purple
Bright Magenta(13):   #FF92D0  ████████  Lighter pink
Bright Cyan   (14):   #9AEDFE  ████████  Lighter cyan
Bright White  (15):   #E6E6E6  ████████  Near white
```

### Syntax Highlighting Colors

```
Function:         #50FA7B  ████████  Green
Class/Type:       #8BE8FD  ████████  Cyan
Constant:         #BD93F9  ████████  Purple
String:           #F1FA8C  ████████  Yellow
Number:           #BD93F9  ████████  Purple
Keyword:          #FF79C6  ████████  Pink
Operator:         #FF79C6  ████████  Pink
Variable:         #F8F8F2  ████████  Foreground
Error:            #FF5555  ████████  Red
Warning:          #FFB86C  ████████  Orange (not in palette, use yellow)
```

### UI Elements

```
Cursor BG:        #F8F8F2  ████████  Foreground color
Cursor FG:        #282936  ████████  Background color (inverted)
Highlight BG:     #44475A  ████████  Selection background
Highlight FG:     #F8F8F2  ████████  Foreground color
Badge:            #BD93F9  ████████  Purple (Tilix custom)
Bold:             #FFFFFF  ████████  Pure white (Tilix custom)
```

## Color Comparison Chart

### Background Variants
```
Terminal BG:      #282936  (Official Dracula background)
Alternative BG:   #1e1f29  (Darker variant - not in official scheme)
Selection:        #44475A  (18% lighter than background)
```

### Transparency Recommendations
```
0%  = #282936  Fully opaque (default)
5%  = #282936  + 95% opacity   (subtle)
10% = #282936  + 90% opacity   (recommended)
15% = #282936  + 85% opacity   (noticeable)
20% = #282936  + 80% opacity   (transparent)
25% = #282936  + 75% opacity   (very transparent)
30% = #282936  + 70% opacity   (heavy transparency)
40% = #282936  + 60% opacity   (maximum usability)
```

## RGB/RGBA Values

For compositor or alpha channel calculations:

```
Background RGB:   rgb(40, 41, 54)
               @ 90% opacity: rgba(40, 41, 54, 0.90)
               @ 85% opacity: rgba(40, 41, 54, 0.85)

Foreground RGB:   rgb(248, 248, 242)
Selection RGB:    rgb(68, 71, 90)
```

## Complete Palette Array (for dconf)

```ini
palette=['#000000', '#FF5454', '#50FA7B', '#F1FA8C', '#BD93F9', '#FF79C6', '#8BE8FD', '#BFBFBF', '#4D4D4D', '#FF6E67', '#5AF78D', '#F4F99D', '#CAA8FA', '#FF92D0', '#9AEDFE', '#E6E6E6']
```

Formatted:
```
[
  '#000000',  // 0:  Black
  '#FF5454',  // 1:  Red
  '#50FA7B',  // 2:  Green
  '#F1FA8C',  // 3:  Yellow
  '#BD93F9',  // 4:  Blue (Purple)
  '#FF79C6',  // 5:  Magenta (Pink)
  '#8BE8FD',  // 6:  Cyan
  '#BFBFBF',  // 7:  White
  '#4D4D4D',  // 8:  Bright Black
  '#FF6E67',  // 9:  Bright Red
  '#5AF78D',  // 10: Bright Green
  '#F4F99D',  // 11: Bright Yellow
  '#CAA8FA',  // 12: Bright Blue (Purple)
  '#FF92D0',  // 13: Bright Magenta (Pink)
  '#9AEDFE',  // 14: Bright Cyan
  '#E6E6E6'   // 15: Bright White
]
```

## Testing Colors in Terminal

Test each color with these commands:

```bash
# Test all 16 ANSI colors
for i in {0..15}; do
    printf "\e[48;5;${i}m  %3d  \e[0m " "$i"
    [ $((($i + 1) % 8)) -eq 0 ] && echo
done

# Test foreground colors
echo -e "\e[30mBlack\e[0m \e[31mRed\e[0m \e[32mGreen\e[0m \e[33mYellow\e[0m"
echo -e "\e[34mBlue\e[0m \e[35mMagenta\e[0m \e[36mCyan\e[0m \e[37mWhite\e[0m"
echo -e "\e[90mBright Black\e[0m \e[91mBright Red\e[0m \e[92mBright Green\e[0m \e[93mBright Yellow\e[0m"
echo -e "\e[94mBright Blue\e[0m \e[95mBright Magenta\e[0m \e[96mBright Cyan\e[0m \e[97mBright White\e[0m"

# Test bold
echo -e "\e[1mBold text\e[0m Normal text"

# Test with sample code
cat << 'CODE'
def hello_world():
    """Print hello world"""
    message = "Hello, Dracula!"
    print(message)
    return 0
CODE
```

## Color Usage Guidelines

### When to Use Each Color

**Green (#50FA7B):**
- Success messages
- Functions and methods
- Strings in some contexts
- Active/running status

**Cyan (#8BE8FD):**
- Classes and types
- Constants
- File paths
- Informational messages

**Purple (#BD93F9):**
- Keywords (if, while, for)
- Numbers and literals
- Special values (true, false, null)

**Pink (#FF79C6):**
- Operators
- Language keywords
- Special symbols
- Import/include statements

**Yellow (#F1FA8C):**
- Strings
- Documentation
- Warnings (when orange not available)
- Highlights

**Red (#FF5454):**
- Errors
- Deletions
- Critical warnings
- Invalid syntax

**Comment Gray (#6272A4):**
- Comments (not in 16-color palette, rendered as bright black)
- Disabled elements
- Secondary information

## Accessibility Notes

### Contrast Ratios (WCAG AA Compliance)

```
Foreground on Background:
  #F8F8F2 on #282936 = 12.6:1  ✓ AAA (excellent)

Green on Background:
  #50FA7B on #282936 = 10.3:1  ✓ AAA (excellent)

Cyan on Background:
  #8BE8FD on #282936 = 8.9:1   ✓ AAA (excellent)

Yellow on Background:
  #F1FA8C on #282936 = 11.2:1  ✓ AAA (excellent)

Pink on Background:
  #FF79C6 on #282936 = 5.4:1   ✓ AA (good)

Purple on Background:
  #BD93F9 on #282936 = 5.8:1   ✓ AA (good)

Red on Background:
  #FF5454 on #282936 = 4.8:1   ✓ AA (acceptable)
```

All colors meet WCAG AA standards for normal text (4.5:1).
Most colors meet AAA standards (7:1).

### Colorblind Considerations

Dracula theme is relatively colorblind-friendly:
- High contrast between background and foreground
- Distinct brightness levels between colors
- Red and green have different brightness (helps with red-green colorblindness)

## Related Themes and Variants

### Dracula Variants
- **Dracula** (this theme): #282936 background
- **Dracula Pro**: Premium variant with additional color schemes
- **Dracula Soft**: Lower contrast variant

### Compatible Themes
These GTK/system themes pair well with Dracula terminal:
- Dracula GTK theme
- Dracula icons
- Papirus-Dark icons (with Dracula folder colors)
- Dracula cursor theme

## References

- [Official Dracula Specification](https://draculatheme.com/spec)
- [Dracula for Tilix](https://draculatheme.com/tilix)
- [GitHub: dracula/tilix](https://github.com/dracula/tilix)
- [Color Contrast Checker](https://webaim.org/resources/contrastchecker/)
- [WCAG Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

---

**Note:** This reference is based on the official Dracula theme specification.
Some applications may use slightly different variants or additional colors.
Always refer to the official spec for the most up-to-date color values.
