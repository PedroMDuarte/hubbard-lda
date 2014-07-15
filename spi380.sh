#!/bin/bash

# Optimal atom numbers 
# 200.  1.5
# 290.  1.7 
# 380.  1.79
# 470   1.84 

python spi_vs_n.py 380. 0.53 --inhomog --savedir dataplots/SPI/380/ \
    --mu -0.11 0. 0.05 0.10 0.13 0.16 --best 2 --spiextents 19 --entextents 18
python spi_vs_n.py 380. 0.56 --inhomog --savedir dataplots/SPI/380/ \
    --mu -0.11 0. 0.05 0.10 0.13 0.16 --best 2 --spiextents 20 --entextents 20
python spi_vs_n.py 380. 0.62 --inhomog --savedir dataplots/SPI/380/ \
    --mu -0.11 0. 0.05 0.10 0.13 0.16 --best 2 --spiextents 23 --entextents 23
python spi_vs_n.py 380. 0.68 --inhomog --savedir dataplots/SPI/380/ \
    --mu -0.11 0. 0.05 0.10 0.13 0.16 --best 2 --spiextents 25 --entextents 25
python spi_vs_n.py 380. 0.80 --inhomog --savedir dataplots/SPI/380/ \
    --mu -0.11 0. 0.05 0.10 0.13 0.16 --best 2 --spiextents 27 --entextents 27
python spi_vs_n.py 380. 0.99 --inhomog --savedir dataplots/SPI/380/ \
    --mu -0.11 0. 0.05 0.10 0.13 0.16 --best 2 --spiextents 28 --entextents 28
python spi_vs_n.py 380. 1.99 --inhomog --savedir dataplots/SPI/380/ \
    --mu -0.11 0. 0.05 0.10 0.13 0.16 --best 2 --spiextents 28 --entextents 28

