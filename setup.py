from setuptools import setup

setup(
    name='unisanews',
    version='0.1',
    description='Twitter and RSS feed creator from Universita\' di Salerno newspage',
    author='Alessandro Ricchiuti',
    author_email='ale DOT ricchiuti AT hotmail DOT it',
    packages=['unisanews'],
    include_package_data=True,
    install_requires=[
        'flask',
        'bs4'
    ]
)
