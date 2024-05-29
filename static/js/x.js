let base
let eixo
let tubo

let inconsolata
let data = {}
let date, hour, ah, dec, cup, tube


async function getJSONData() {
  data = await loadJSON('assets/data.json')
}


function preload() {
  base = loadModel("static/assets/Base_Pilar.obj", false)
  eixo = loadModel("static/assets/Eixo_RA_DEC.obj", false)
  tubo = loadModel("static/assets/Tubo_BC24.obj", false)
  inconsolata = loadFont('static/assets/inconsolata.otf')
  data = loadJSON('static/assets/data.json')
  setInterval(getJSONData, 1000)
}


function setup() {
  createCanvas(windowWidth, windowHeight, WEBGL)
  textFont(inconsolata)
  textSize(height / 40)
  textAlign(CENTER, CENTER)

}

function draw() {
  background(180)
  box(1);

  if (data['hour']) {  // Atualiza o valor apenas se ele realmente existir. Ação para que não apareça 'UNDEFINED' como resultado
    hour = data['hour']
    ah = data['ah']
    dec = data['dec']
    date = data['date']
  }

  fill(255,0,255) // Atribui cor ao modelo
  text('\nBC24-IAG\n' + 'Date:' + date + '\n' + 'Hour:' + hour + '\n\n' + 'AH:' + ah + '\n' + 'DEC:' + dec, 100, 100)
  text('\nra_deg: ' + ra_deg() + '\ndec_deg: ' + dec_deg(), 100, 320)


  scale(.15)
  normalMaterial()
  fill(255,255,0) // Atribui cor ao modelo
  stroke(1)

  rotateY(-120 * PI / 180)
  translate(0, 0, 1785) //Offset para evidenciar a escrita

  let DEC = dec_deg()
  let RA_deg = ra_deg()

  rotateX(-202.5 * PI / 180) // É nessa linha que sera somado 22.5 graus
  model(base)
  //rotateZ(-millis() / 1000 * PI / 180 / 240) // Isso gira o RA ou sideral
  rotateZ(-RA_deg * PI / 180) // Aqui configura o valor do Eixo RA (+/-4,5 ah)

  translate(0, 0, 1785) //Offset para coincidir os pivôs da base e do eixo

  model(eixo)
  translate(223.24, 0, 0) //Offset para coincidir os pivôs do eixo e do tubo
  rotateX(22.5 * PI / 180)  // Aqui configura a Latitude
  rotateX(-1 * (DEC + 22.53) * PI / 180)  // Aqui configura o valor do eixo DEC (+57 N e -80 S)
  model(tubo)


}


function ra_deg() {

  ra_result = float(abs(ah.split(" ")[0] * 15)) + float(ah.split(" ")[1] / 60 * 15) + float(ah.split(" ")[2] / 3600 * 15)

  if (ah.split(" ")[0] + 0.5 < 0) { // Atificio para detectar valor negativo
    ra_result = -ra_result
  }

  return ra_result
}

function dec_deg() {

  dec_result = float(abs(dec.split(" ")[0])) + float(dec.split(" ")[1] / 60) + float(dec.split(" ")[2] / 3600)

  if (dec.split(" ")[0] < 0) {
    dec_result = -dec_result
  }

  dec_result = dec_result + 22.53

  return dec_result
}