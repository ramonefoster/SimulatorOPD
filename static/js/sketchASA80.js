let base
let fork
let tubo

let inconsolata
let data = {}
let date, hour, ah, dec, cup, tube, alt, az
let az_slider
let alt_slider
let multi_slider_size = 150

async function getJSONData() {
    try {
      const response = await fetch('http://127.0.0.1:5000/api/telescope/position');
      data = await response.json();
      
    } catch (error) {
      console.error('Error:', error);
    }
  }


function preload() {
  base = loadModel("static/assets/asa80/Base.obj", false)
  fork = loadModel("static/assets/asa80/Fork.obj", false)
  tubo = loadModel("static/assets/asa80/Tube.obj", false)
  inconsolata = loadFont('static/assets/inconsolata.otf')
  setInterval(getJSONData, 1000)
}


function setup() {
    createCanvas(windowWidth, windowHeight, WEBGL)
    textFont(inconsolata)
    textSize(height / 45)
    textAlign(CENTER, CENTER)
  
    color_slider = createSlider(50, 150, 100);
    color_slider.position(10, 820)
    color_slider.style('width', multi_slider_size + 'px');
  
  }

let value = -180;

function mouseDragged() {
  value = mouseX;
}

function draw() {
  background(color_slider.value())

translate(0, 150, 0)
  if (data) {  // Atualiza o valor apenas se ele realmente existir. Ação para que não apareça 'UNDEFINED' como resultado
    ah = data.hour_angle
    dec = data.declination
    alt = data.elevation
    az = data.azimuth
  }

  fill(150, 0, 100)
  noFill()

  scale(.18)
  normalMaterial()
  fill(34, 36, 58) // Atribui cor ao modelo
  stroke(1)

//   rotateY(value * PI / 180)

  rotateX(-180 * PI / 180) // inverte-se o modelo
  model(base)
  rotateY(az* PI / 180) // Aqui configura o valor do Eixo AZ
 
  model(fork)
  translate(0, 971, 0) //Offset para coincidir os pivôs do fork e do tubo
  rotateX((90-alt)*PI / 180)
  fill(140, 154, 164)
  model(tubo)
  ortho();
  
}


function windowResized() {
  resizeCanvas(windowWidth, windowHeight);
}