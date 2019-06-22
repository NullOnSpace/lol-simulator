## LOL Simulator

#### Progress and Plan
* *basic champion statistics*
* **basic items property**
* *basic mechanism functions*
* functions for champion abilities
* functions for item interactive property
* calculate damage amount from a group of champion abilities
 with certain items and given level without regard to time
* take time into consideration

### Basic Champion Statics

- To Do List
- [ ] update database base on html files 

- Problems So Far 
- [ ] need a proper way to classify champions' resource
- [ ] need a proper way to record the champions with multi-values in a single property


### Basic Items Statics

- To Do List
- [x] build up database base on data

- Problems So Far
- [x] two forms of ap, mana. exa: "10", "10 - 180 (based on level)"  
**extra fields for different forms** 
- [x] two forms of move speed. exa: "10", "5%"  
**extra fields for different forms**
- [x] implementation of item recipe in model  
recipe model with 4 ContentType at most


### Basic Mechanism Functions
- [ ] divide champion.attack into cast attack and fist attack
- [ ] create ability class
- [ ] divide champion, projectile, damage into more status
- [ ] create first bunch of triggers


#### Predictable Problems
- [ ] get the shake time before and after attack/cast action
