# Synthesis-Dark Usability Guide

Welcome to the **Synthesis-Dark** infrastructure. This guide ensures you can deploy and utilize the harmonized theme across your entire system.

## 1. Environment Activation

### **GTK Themes**
Apply the theme using your desktop's settings or via command line:
```bash
gsettings set org.mate.interface gtk-theme 'Synthesis-Dark'
gsettings set org.gnome.desktop.interface gtk-theme 'Synthesis-Dark'
```

### **Icon & Cursors**
```bash
gsettings set org.mate.interface icon-theme 'MATE-Synthesis-Dark'
gsettings set org.mate.interface cursor-theme 'MATE-Synthesis-Dark-Cursors'
```

## 2. Terminal Harmonization

### **Alacritty**
Link the provided config:
```bash
mkdir -p ~/.config/alacritty
ln -sf ~/Github/Synthesis-Dark/extras/alacritty/alacritty.toml ~/.config/alacritty/alacritty.toml
```

### **Tilix**
Import the scheme in Tilix Preferences -> Color Schemes -> Import.

## 3. Editor Integration

### **Micro**
```bash
mkdir -p ~/.config/micro/colorschemes
ln -sf ~/Github/Synthesis-Dark/extras/micro/synthesis-dark.micro ~/.config/micro/colorschemes/
```
In micro, press `Ctrl-E` and type `set colorscheme synthesis-dark`.

## 4. Maintenance
To rebuild all assets and verify color consistency after an update:
```bash
./src/build.sh
```

---
**Note:** For Arch Linux users, the `PKGBUILD` in the root directory automates the installation of all components.
