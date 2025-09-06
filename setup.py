from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="smartleakpro",
    version="1.0.0",
    author="SmartLeakPro Team",
    author_email="contact@smartleakpro.com",
    description="Application web de gestion centralisée des clients, interventions et rapports d'inspection pour la détection de fuites",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/votre-username/SmartLeakPro",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: Django",
        "Framework :: Django :: 4.2",
    ],
    python_requires=">=3.8",
    install_requires=[
        "Django>=4.2.7",
        "djangorestframework>=3.14.0",
        "django-cors-headers>=4.3.1",
        "django-filter>=23.3",
        "django-extensions>=3.2.3",
        "djangorestframework-simplejwt>=5.3.0",
        "Pillow>=10.0.1",
    ],
)
