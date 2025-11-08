name: Generate Distinct Mob Sounds MP3

on:
  workflow_dispatch:

jobs:
  generate_mob_sounds:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      - name: Install dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y sox lame git jq

      - name: Generate distinct noise sounds
        run: |
          mkdir -p sounds
          declare -a mobs=("phyle" "troivjuer" "nihdun")
          declare -a types=("idle" "hurt" "death")
          for mob in "${mobs[@]}"; do
            for type in "${types[@]}"; do
              case $type in
                idle) vol=0.3 len=1 ;;
                hurt) vol=0.5 len=1.5 ;;
                death) vol=0.7 len=2 ;;
              esac
              fname="sounds/${mob}_${type}.wav"
              case $mob in
                phyle)
                  sox -n -r 44100 -c 2 "$fname" synth $len whitenoise vol $vol
                  ;;
                troivjuer)
                  sox -n -r 44100 -c 2 "$fname" synth $len tri vol $vol
                  ;;
                nihdun)
                  sox -n -r 44100 -c 2 "$fname" synth $len saw vol $vol
                  ;;
              esac
              lame -V2 "$fname" "${fname%.wav}.mp3"
              rm "$fname"
            done
          done

      - name: Generate sounds.json for Minecraft
        run: |
          mkdir -p assets/myaddon/sounds
          echo -n "{" > assets/myaddon/sounds/sounds.json
          declare -a mobs=("phyle" "troivjuer" "nihdun")
          declare -a types=("idle" "hurt" "death")
          first=true
          for mob in "${mobs[@]}"; do
            for type in "${types[@]}"; do
              [ "$first" = true ] && first=false || echo -n "," >> assets/myaddon/sounds/sounds.json
              echo -n "\"${mob}.${type}\": {\"sounds\":[\"myaddon:${mob}_${type}\"]}" >> assets/myaddon/sounds/sounds.json
            done
          done
          echo -n "}" >> assets/myaddon/sounds/sounds.json

      - name: Commit and push
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add sounds/*.mp3 assets/myaddon/sounds/sounds.json
          git pull
          git commit -m "Generate distinct mob noises MP3 and sounds.json"
          git push
