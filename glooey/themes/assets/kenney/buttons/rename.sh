#!/usr/bin/env bash

for d in $(ls); do (
    cd $d
    mv high high_gloss
    mv low low_gloss
    mv none matte
) done
