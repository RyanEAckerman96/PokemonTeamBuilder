# PokemonTeamBuilder


Architecture
 
  CustomDataType
        PokemonData:
          name
          types
          sprite_url
          create_time

      UserData
          username
          password
          Team

      Team -> List of PokemonData


  Backend:
    Two Main Threads:
      Scraper:
        Scraper loads pokemon_db from a pickle file
        pokemon_db is just a mapping of ID to PokemonData

        Thread will then loop over ids and scrap the Pokémon api
        Once it completed all entries, it will sleep and restart process

        Upon shutdown current state of pokemon_db is written to pickle file

      Websocket:
        Websocket loads user_db from a pickle file
        user_db is just a mapping of Username to UserData

        Thread will then open socket, and handle requests from connected clients.
        Communication is done via JSON, protocol will be specified below.

        When user logons, the login session is tied directly to the WS connection.

        upon shutdown current state of user_db is written to pickle file.

  Main concerns 
    With the two thread is that race conditions would exists with the pokemon_db.
    While a race condition does exists. All read/write operations to the DB are atomic so clients can not have the backend read corrupted data.
    If a client is viewing a team at the same moment the API changes one of the pokemon in the team. That information is not notified to the front end until the team is requested again

    Future improvements:
      The Server should have all the info it needs to know who is logged in, teams for that user, and what pokemon are in that team, So it should be able to push a notification to the Frontend to let users know of a change
      I would prefer if the User Data portion is stored in an actual SQL database, and have the authentication of a user abstracted to a different API. 
      Then make a change where each request requiring user data must authenticate. Leaving the Front end free to maintains cookies of the logon credentials or something.

      It would be good to at a set interval write out the dbs to their pickle files, to safe guard the data from being lost upon an unexpected shutdown



  Frontend:
    Standard HTML & java script webpage

    Javascript connect to backend Server, and submit request over a JSON Protocol.

    Main Concerns:
      Because this is a normal "WS" connection there is basically no security exists. Password are passed in plain text. 
      Sessions are tied directly to the connection itself. A refresh will "log out"

    Future Improvements:
       Have Cookies keep login info, and split into a login & register page and the main builder page. To allow the user to got forward and back.
       
   



Server -> Client Communications
    All messages will be in a wrapper

    {
      "status":200/404
      "responding":""
      "info":{}
    }

    "status": 200 indicate a success
    "status": 404 indicates an error

    "responding":"" will return the context in which this response was generated 
    
    In control messages like all 404 and certain 200s.
    Will be as below:
      "info" : { "text":""}

    This will have any error reasoning or the text "success" to let the client know an operation completed if data is not required to be sent to the client



Requests
  "register"

    Registers user
    if Passwords to not match or User already exists Server sends 404
    otherwise sends 200

  "logon"

    Log user in
    If user is not in user_db or the password is not correct sends 404
    otherwise sends 200


  "get_pokemon"
    given an ID & the position the pokemon will be in the team
    returns 200 with info that contains the position and the PokemonData

    If ID does not matchup to a known pokemon return 404

  "load_teams"
    if a name is provided
       returns a 200 with info that contains the name of the team and two Pokémon teams
           first team is the saved team
           second team is the team as pulled from the pokemon_db

        if the name does not exists it return a 404

    If name is not provided
      returns a 200 with a list of all names of team assossiated with user

    For both if the user does not exists or the logged in user for the WS connection is not the user it will send a 404

    "save_team"
      

    


        
