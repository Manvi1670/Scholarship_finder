const jwt = require('jsonwebtoken')

const midwareFunc = (req, res, next) => {
  let jwtToken
  // console.log(req.headers)
  const auth = req.headers['authorization']
  if (auth !== undefined) {
    jwtToken = auth.split(' ')[1]
  }
  if (jwtToken === undefined) {
    res.status(401)
    res.send('Invalid JWT Token')
  } else {
    jwt.verify(jwtToken, 'MY_SECRET_TOKEN', async (error, payload) => {
      if (error) {
        res.status(401)
        res.send('Invalid JWT Token')
      } else {
        req.user = payload
        next()
      }
    })
  }
}

module.exports = midwareFunc;