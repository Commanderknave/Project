openapi: 3.0.3
info:
  title: CS3103 A5 Steam Gift Registry
  description: |-
    This is a gift registry API flavored in the shape of
    a stean wishlist.

    We will be using the steamdb.info/app/{id} to access 
    our data of different games.

    Example:
    - (https://steamdb.info/app/2246340/)
  version: 1.0.0
  contact:
    email: ivanderp@unb.ca
tags:
  - name: user
    description: User operations
  - name: game
    description: Game operations
  - name: friends
    description: Friend operations
  - name: pre-user
    description: Operations that happen before a user is a user
paths:
  /user/login:
    post:
      tags:
        - Users
      summary: Log User into system
      description: ''
      operationId: loginUser
      requestBody:
        description: Username and password
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Login'
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User_Details'
        '400':
          description: Invalid Request
  /user/logout:
    get:
      tags:
        - Users
      summary: Log out current user
      description: ''
      operationId: logoutUser
      responses:
        '200':
          description: Success
        '400':
          description: Invalid Request
  /user/register:
    post:
      tags:
        - Users
      summary: Register a new user
      description: ''
      operationId: registerUser
      requestBody:
        description: User information
        content:
          application/json:
            schema:
              type: object 
              properties:
                username:
                  type: string
                  example: JoeMama
                user_password:
                  type: string
                  example: password123
                email:
                  type: string
                  example: joemama@place.com
        required: true 
      responses:  
        '201':
          description: User Created
        '400':
          description: Invalid Request
  /user/validate/{id}:
    get:
      tags:
        - Users
      summary: Validate user
      description: ''
      operationId: validateUser
      parameters:
        - name: id
          in: path
          description: Hash of user to validate
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Success
        '400':
          description: Invalid Request
        '408':
          description: Request Timeout
  /user/{id}:
    get:
      tags:
        - Users
      summary: Get user by ID
      description: ''
      operationId: getUserById
      parameters:
        - name: id
          in: path
          description: ID of user to return
          required: true
          schema:
            type: integer
            format: int64
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User_Details'
        '400':
          description: Invalid Request
        '404':
          description: User not found
  /user/recentLogins:
    get:
      tags:
        - Users
      summary: Get list of recent logins
      description: ''
      operationId: fetchRecentLogins
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/RecentLogins'
        '400':
          description: Invalid Request
  /user/settings:
    get:
      tags:
        - Users
      summary: Get user settings
      description: ''
      operationId: getUserSettings
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User_Settings'
        '400':
          description: Invalid Request
        '404':
          description: User not found
  /user/fetchUserByName/{username}:
    get:
      tags:
        - Users
      summary: Get user by username
      description: ''
      operationId: getUserByUsername
      parameters:
        - name: username
          in: path
          description: Username of user
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User_Details'
        '404':
          description: User not found
  /user/forgotPassword:
    post:
      tags:
        - Users
      summary: User to request email to change password
      description: ''
      operationId: updatePassword
      requestBody:
        description: Email to request password change
        content:
          application/json:
            schema:
              type: object
              properties:
                email:
                  type: string
                  example: joemama@place.com
        required: true
      responses:
        '200':
          description: Success
        '404':
          description: Email does not exist
  /user/newPassword/{email_Hash}:
    post:
      tags:
        - Users
      summary: User to change password
      description: ''
      operationId: changePassword
      parameters:
        - name: email_Hash
          in: path
          description: Hash of email sent to change password
          required: true
          schema:
            type: string
      requestBody:
        description: New password
        content:
          application/json:
            schema:
              type: object
              properties:
                user_password:
                  type: string
                  example: password123
        required: true
      responses:
        '200':
          description: Success
        '404':
          description: Email does not exist
        '408':
          description: Request Timeout
  /game/{id}:
    get:
      tags:
        - Games
      summary: Get game by ID
      description: ''
      operationId: getGameById
      parameters:
        - name: id
          in: path
          description: ID of game to return
          required: true
          schema:
            type: integer
            format: int64
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Game'
        '404':
          description: Game not found
  /game/addGame:
    post:
      tags:
        - Games
      summary: Add a game to the database
      description: ''
      operationId: addGame
      requestBody:
        description: Game information
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Game'
        required: true
      responses:
        '201':
          description: Game Created
        '400':
          description: Invalid Request
  /game/wish/{id}:
    post:
      tags:
        - Games
      summary: Add game to current user's wishlist
      description: ''
      operationId: wishGame
      parameters:
        - name: id
          in: path
          description: ID of game to add to wishlist
          required: true
          schema:
            type: integer
            format: int64
      responses:
        '200':
          description: Success
        '304':
          description: Game already in wishlist
        '400':
          description: Invalid Request
        '404':
          description: Game not found
  /game/removeWish/{id}:
    delete:
      tags:
        - Games
      summary: Remove game from current user's wishlist
      description: ''
      operationId: removeWish
      parameters:
        - name: id
          in: path
          description: ID of game to remove from wishlist
          required: true
          schema:
            type: integer
            format: int64
      responses:
        '200':
          description: Success
        '400':
          description: Invalid Request
        '404':
          description: Game not found
  /game/wishlist/{id}:
    get:
      tags:
        - Games
      summary: Get wishlist of user by ID
      description: ''
      operationId: getWishlist
      parameters:
        - name: id
          in: path
          description: ID of user to return wishlist
          required: true
          schema:
            type: integer
            format: int64
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Wishlist'
        '400':
          description: Invalid Request
        '404':
          description: User not found
  /game/purchase/{id}/{game_id}:
    put:
      tags:
        - Games
      summary: Purchase game for user
      description: ''
      operationId: purchaseGame
      parameters:
        - name: id
          in: path
          description: ID of user to purchase game for
          required: true
          schema:
            type: integer
            format: int64
        - name: game_id
          in: path
          description: ID of game to purchase
          required: true
          schema:
            type: integer
            format: int64
      responses:
        '200':
          description: Success
        '400':
          description: Invalid Request
        '404':
          description: User or Game not found
  /friends/{id}:
    get:
      tags:
        - Friends
      summary: Get friends list of user by ID
      description: ''
      operationId: getFriendsList
      parameters:
        - name: id
          in: path
          description: ID of user to return friends list
          required: true
          schema:
            type: integer
            format: int64
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/FriendsList'
        '400':
          description: Invalid Request
        '404':
          description: User not found
  /friends/addFriend/{id}:
    post:
      tags:
        - Friends
      summary: Add friend to current user's friends list
      description: ''
      operationId: addFriend
      parameters:
        - name: id
          in: path
          description: ID of friend to add
          required: true
          schema:
            type: integer
            format: int64
      responses:
        '200':
          description: Success
        '304':
          description: Friend already in friends list
        '404':
          description: Friend not found
  /friends/removeFriend/{id}:
    delete:
      tags:
        - Friends
      summary: Remove friend from current user's friends list
      description: ''
      operationId: removeFriend
      parameters:
        - name: id
          in: path
          description: ID of friend to remove
          required: true
          schema:
            type: integer
            format: int64
      responses:
        '200':
          description: Success
        '404':
          description: Friend not found
components:
  schemas:
    Login:
      type: object
      properties:
        username:
          type: string
          example: JoeMama
        user_password:
          type: string
          example: password123
      required:
        - username
        - user_password
    RecentLogins:
      type: array
      items:
        oneOf:
          - $ref: '#/components/schemas/User_Details'
    User_Details:
      type: object
      properties:
        id:
          type: integer
          format: int64
          example: 1
        username:
          type: string
          example: JoeMama
        email:
          type: string
          example: joemama@place.com
        creation_date:
          type: string
          example: 01/01/2025 00:00:00 UTC
        last_login:
          type: string
          example: 01/01/2025 00:00:00 UTC
    User:
      type: object
      properties:
        id:
          type: integer
          format: int64
          example: 1
        username:
          type: string
          example: JoeMama
        user_password:
          type: string
          example: password123
        email:
          type: string
          example: joemama@place.com
        creation_date:
          type: string
          example: 01/01/2025 00:00:00 UTC
        last_login:
          type: string
          example: 01/01/2025 00:00:00 UTC
    User_Settings:
      type: object
      properties:
      # Could be more or less here
        background_color:
          type: string
          example: #000000
        font_color:
          type: string
          example: #FFFFFF
        font_size:
          type: string
          example: small
    Game:
      type: object
      properties:
        id:
          type: integer
          format: int64
          example: 1
        name:
          type: string
          example: Monster Hunter Wilds
        steam_id:
          type: integer
          example: 2246340
        url:
          type: string
          example: https://store.steampowered.com/app/2246340/
        price:
          type: number
          example: 89.99
        description:
          type: string
          example: A game where you hunt monsters
        developer:
          type: string
          example: Capcom
        publisher:
          type: string
          example: Capcom
        release_date:
          type: string
          example: 01/01/2025
        thumbnail:
          type: string
          example: https://store.steampowered.com/app/2246340/nameOfImage.jpg
    Wishlist:
      type: array
      items:
        oneOf:
          - $ref: '#/components/schemas/Game'
    FriendsList:
      type: array
      items:
        oneOf:
          - $ref: '#/components/schemas/User_Details'
        
