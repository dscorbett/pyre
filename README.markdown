Pyre is a program that simulates language change with [features](http://en.wikipedia.org/wiki/Distinctive_feature). At least, that is what it will do. Right now it is a program that catalogues phonemes and features.

To run, download and run the file `pyre.py`. After the debugging information, type a command at the prompt. It understands the following inputs:

* `<phonemes> = <features>` (e.g.&nbsp;`i y=+high -back +syll`)

  Create the specified phonemes with the specified features. All features are binary. You are not allowed to changed the value of a feature once it has been set, but you can always add additional features.

  Phonemes can be enclosed in slashes to mean "all the features of this phoneme". For example, if /t/ has already been defined as [+coronal &minus;sonorant &minus;voice], then `d=/t/+voice` would create /d/ as [+coronal &minus;sonorant +voice].

* `<features> : <phonemes>` (e.g.&nbsp;`+voice -nasal: b d g`)

  This is the same as the previous input, but with the phonemes and features reversed.

Planned features:

* Implications, e.g.&nbsp;[&minus;sonorant] &#x2192; [&minus;voice]

* Sound change rules