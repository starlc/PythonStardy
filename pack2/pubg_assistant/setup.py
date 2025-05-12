from setuptools import setup, find_packages

setup(
    name="pubg_assistant",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pynput>=1.7.6",
        "opencv-python>=4.5.5.64",
        "numpy>=1.20.0",
        "pyttsx3>=2.90",
        "mss>=6.1.0",
        "Pillow>=9.0.0",
    ],
    entry_points={
        'console_scripts': [
            'pubg-assistant=pubg_assistant.main:main',
        ],
    },
    author="PUBG Assistant Team",
    author_email="example@example.com",
    description="PUBG游戏辅助工具",
    keywords="pubg, assistant, gaming",
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Gamers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
) 