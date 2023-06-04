# Tool Artifacts 

This repository contains additional material for the paper entitled **Ontology-driven Automated Reasoning about Property Crimes**  that shows a set of tool that uses information extraction techniques to obtain the data from the police reports, guided by an ontology that we have developed for the Spanish legal system on property crimes. Probabilistic inference mechanisms are used to select the set of articles of the law that could apply to a given case, even when the evidence does not allow an unambiguous identification.

This folder contains all artifacts developed in the project, including the SPCO Ontology with evaluation examples extracted and inferred , the neo4j sentences to load example rdf's evaluated into neo4j, and etc.


## Structure

The contents of this repository as organized as follows:

* SCPO Ontology: an Ontology for Spanish Property Crimes and samples of anonymised police reports for reproducibility purposes
* Neo4jOntolgyLibrary: Code that applies the probabilistic inference mechanisms used to select the set of articles of law that could apply to a given case
* Loading example rdf's evaluated into Neo4j 
* Sentences: to calculate the probability that an item applies to a given case

## SCPO Ontology

It consists first of an owl file in turtle format that implements the property crime ontology. It also contains two folders with the evaluated examples. The first one contains the extracted rdf files and the second one the rdf's inferred by applying the ontology with the pellet inference engine. 


## Neo4jOntolgyLibrary

The repository includes the code implemented to apply an article of law to a given case and calculate the probabylity inferred.  .

### Requirements/dependencies

The code is provided as a Maven project, which has been developed in Apache Netbeans IDE 16 with Java 11.

The following dependecies are required:

* [Neo4j community edition version 4.3.2](https://neo4j.com/download-center/#community), a  graph database  management  system  with CRUD methods that expose a graph data model. This version uses a java implementation with Java 11.
* [Apoc Core plugin](https://neo4j.com/labs/apoc/4.1/installation) The APOC library consists of many  procedures and functions to help with many different tasks in areas like data integration, graph algorithms or data conversion.

In in order to facilitate the configuration of Neo4j I show you the essential configuration elements of ne4j configuration to be able to test all the experiments. The 

At least the following lines in the neo4j.conf file (in the case of linux from the Archlinux distribution /etc/neo4j/neo4j.conf) in the $NEO4J_HOME directory  must be enabled.

```
    # Paths of directories in the installation.
    dbms.directories.data=/var/lib/neo4j/data
    dbms.directories.plugins=/usr/share/java/neo4j/plugins
    dbms.directories.certificates=/etc/neo4j/certificates
    dbms.directories.logs=/var/log/neo4j
    dbms.directories.lib=/usr/share/java/neo4j/lib
    dbms.directories.run=/run/neo4j

    #This setting constrains all `LOAD CSV` import files to be under the `import` directory. Remove or comment it out to
    # allow files to be loaded from anywhere in the filesystem; this introduces possible security problems. See the
    # `LOAD CSV` section of the manual for details.
    dbms.directories.import=/var/lib/neo4j/import

    # Whether requests to Neo4j are authenticated.
    # To disable authentication, uncomment this line
    dbms.security.auth_enabled=false

    # Java Heap Size: by default the Java heap size is dynamically
    # calculated based on available system resources.
    # Uncomment these lines to set specific initial and maximum
    # heap size.
    dbms.memory.heap.initial_size=1G
    dbms.memory.heap.max_size=2G

    # The amount of memory to use for mapping the store files, in bytes (or
    # kilobytes with the 'k' suffix, megabytes with 'm' and gigabytes with 'g').
    # If Neo4j is running on a dedicated server, then it is generally recommended
    # to leave about 2-4 gigabytes for the operating system, give the JVM enough
    # heap to hold all your transaction state and query context, and then leave the
    # rest for the page cache.
    # The default page cache memory assumes the machine is dedicated to running
    # Neo4j, and is heuristically set to 50% of RAM minus the max Java heap size.
    dbms.memory.pagecache.size=3g

    #********************************************************************
    # Other Neo4j system properties
    #********************************************************************
    dbms.jvm.additional=-Dunsupported.dbms.udc.source=tarball
    dbms.unmanaged_extension_classes=n10s.endpoint=/rdf
    dbms.security.procedures.unrestricted=apoc.*
    dbms.logs.query.enabled=true
```
### Install ontology.util plugin
To install the plugin with the Ontology handling procedures and functions in Neo4j we need to

1. Clone the Neo4jOntolgyLibrary project on the machine where it has been installed in Neo4j.
2. Build the project 

```
    cd $HOME_PROJECT
    JAVA_HOME=/... # if is not defined variable $JAVA_HOME the path should be specified
    mvn clean install  
```
3. Copy the file $HOME_PROJECT/target/Neo4jOntologyLibrary-6.2-SNAPSHOT.jar to the $HOME_NEO4J/plugins directory specified in the neo4j.conf file.
4. Restart the neo4j service

## Loading evaluated rdf examples into Neo4j

To simulate the process of constructing knowledge graphs that apply an article of law to a given example and to calculate the inferred probability, the following steps must be followed:

1. First open a browser and connect to the Neo4j client  (with this configuration, no credentials are required)

```
    http://neo4j_server_ip:7474/browser/
    
```  



2.  Load the example file generated by the pellet inference engine after applying the legal ontology. Download [Atestado_Evaluacion_Pellet.owl](https://github.com/atenearesearchgroup/property-crime-classification/blob/main/ToolArtifacts/Sentences/), from the folder of the evaluated example, to evaluated example 01 or 02 ...

```
    CALL n10s.graphconfig.init();
    CALL n10s.rdf.import.fetch("file:///var/lib/neo4j/import/Atestado_Evaluacion_Pellet.owl","Turtle");

```
3. Clean up some auxiliary nodes and relations generated by the inference engine.

```
    MATCH (n)-[r:ns0__ReportProperty]->(p) delete r ;
    MATCH (n)-[r:ns0__CharacteristicProperty]->(p) delete r ;
    MATCH (n)-[r:ns0__PersonProperty]->(p) delete r ;
    MATCH (n)-[r:ns0__TheftThingProp]->(p) delete r ;
    MATCH (n)-[r:rdf__type]->(p) delete r ;

    MATCH (n:ns0__Report)-[r:rdf__type]->(p) 
    where p.name starts with "bnode" delete r ;
  
    MATCH (n) where n.uri is not null set n.uri = null return *;

```

4. Generate a copy of the loaded graph so that it can be compared with an article of law. Download [CargaAtestado_xx_xx_Root.txt](https://github.com/atenearesearchgroup/property-crime-classification/blob/main/ToolArtifacts/Sentences/) or [CargaAtestado_xx_xx_Subgraph.txt](https://github.com/atenearesearchgroup/property-crime-classification/blob/main/ToolArtifacts/Sentences/), from the folder of the evaluated example, to generate the root an the completed copy of the knowledge graph ...

    * Root
    ```
        MATCH (rootA:owl__NamedIndividual {name: 'Atestado_01_22'})
        WHERE rootA.article is null
        call apoc.refactor.cloneNodes([rootA], false) yield output
        with rootA, output
        set output.article = 'ns0_Article234_1'
        return rootA, output;

    ```

    * Subgraph
    ```
        MATCH  (rootA:owl__NamedIndividual {name:'Atestado_01_22'}),
               (rootB:owl__NamedIndividual {name:'Atestado_01_22', article:'ns0_Article234_1'})
        where rootA.article is null
        CALL apoc.path.subgraphAll(rootA, {relationshipFilter:'<|>'})
        YIELD nodes, relationships
        CALL apoc.refactor.cloneSubgraph(
            nodes,
            relationships,
            { standinNodes:[[rootA, rootB]] })
        YIELD input, output, error
        RETURN input, output, error;

    ```

5. Decorate each relation of the evaluated case, using the "ontology.util" library, with the probability associated to the applied item if the relation is necessary, determine the surplus relations and create the necessary non-existing relations. Download [CargaAtestado_xx_xx_addArticlePriorProbability.txt](https://github.com/atenearesearchgroup/property-crime-classification/blob/main/ToolArtifacts/Sentences/), from the folder of the evaluated example, to apply to others articles of the law.

```
    MATCH  (rootA:owl__NamedIndividual {name:'Atestado_01_22', article:'ns0_Article234_1'})
    CALL ontology.util.addArticlePriorProbability(rootA, 'Article234_1')
    YIELD relations
    RETURN relations;

```

6. Calculate the inferred probability of the application of an article of the law in a given case.  Download [CargaAtestado_xx_xx_subGraphProbability.txt](https://github.com/atenearesearchgroup/property-crime-classification/blob/main/ToolArtifacts/Sentences/), from the folder of the evaluated example, to calculate the inferred probability to others articles of the law.

```
    MATCH  (rootA:owl__NamedIndividual {name:'Atestado_01_22', article:'ns0_Article234_1'})
    CALL apoc.path.subgraphAll (rootA, {relationshipFilter:'<|>'})
    YIELD nodes, relationships
    RETURN ontology.util.subGraphProbability (relationships,'Article234_1');

```

## Query evaluated rdf examples into Neo4j

To consult the evaluated rdf examples, please follow the instructions below:

* First open a browser and connect to the Neo4j client  (with this configuration, no credentials are required)

```
    http://neo4j_server_ip:7474/browser/
```  

* Copy the loading file [exampleX.graphml](https://github.com/atenearesearchgroup/property-crime-classification/blob/main/ToolArtifacts/Sentences/), from the folder of the evaluated example, of nodes and relations from the evaluation example into $HOME_NEO4J/import
* Run next statement of the copied graphml file in the Neo4j client

```
    CALL apoc.import.graphml("example1.graphml", {readLabels: true})
```
* Calculate the inferred probability of the application of an article of the law in a given case.  Download [CargaAtestado_xx_xx_subGraphProbability.txt](https://github.com/atenearesearchgroup/property-crime-classification/blob/main/ToolArtifacts/Sentences/), from the folder of the evaluated example, to calculate the inferred probability to others articles of the law.

```
    MATCH  (rootA:owl__NamedIndividual {name:'Atestado_01_22', article:'ns0_Article234_1'})
    CALL apoc.path.subgraphAll (rootA, {relationshipFilter:'<|>'})
    YIELD nodes, relationships
    RETURN ontology.util.subGraphProbability (relationships,'Article234_1');

```


---

**Disclaimer**: This repository is currently under development.  
