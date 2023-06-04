/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package ontology.util;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.neo4j.graphdb.Direction;
import org.neo4j.graphdb.GraphDatabaseService;
import org.neo4j.graphdb.Label;
import org.neo4j.graphdb.Node;
import org.neo4j.graphdb.Relationship;
import org.neo4j.graphdb.RelationshipType;
import org.neo4j.graphdb.Transaction;
import org.neo4j.logging.Log;
import org.neo4j.procedure.Context;
import org.neo4j.procedure.Description;
import org.neo4j.procedure.Mode;
import org.neo4j.procedure.Name;
import org.neo4j.procedure.Procedure;
import org.neo4j.procedure.UserFunction;

/**
 *
 * @author fjnavarrete
 */
public class ReportOntology {
    
    
    // This field declares that we need a GraphDatabaseService
    // as context when any procedure in this class is invoked
    @Context
    public GraphDatabaseService db;
    
    @Context 
    public Transaction tx;
    
    // This gives us a log instance that outputs messages to the
    // standard log, normally found under `data/log/console.log`
    @Context
    public Log log;
    
    @Procedure(value = "ontology.util.addArticlePriorProbability" , mode = Mode.WRITE)
    @Description("ontology.util.addArticlePriorProbability(.....")
    public Stream<RelationshipProbabilities> addArticlePriorProbability(
            @Name("node") Node node, 
            @Name("article") String article                                      
            ){

        if (node == null ) throw new IllegalArgumentException("Nodes is Null");
        if (article == null ) throw new IllegalArgumentException("Article is Null");
        LinkedHashSet<Relationship> relation = new LinkedHashSet<>();
        List<String> probabilities = new ArrayList();
        defineArticlePriorProbability(node, article, article, relation);
        List<Relationship> r = new ArrayList<>();
        r.addAll(0, relation);
        return Stream.of(new RelationshipProbabilities(r, probabilities));
    }
    
    @UserFunction(value = "ontology.util.subGraphProbability")
    @Description("ontology.util.subGraphProbability(.....")
    public List<String> subGraphProbability(
            @Name("node") List<Relationship> relations, 
            @Name("article") String article                                      
            )
    {
        LinkedHashSet<String> necessary = new LinkedHashSet<>();
        String TheftPerpretator = "";
        String Stolengoods = "";
        String BurglaryCrime = "";
        String HouseOrPremiseBreaking = "";
        String RobberyWithIntimidationOrViolence = "";
        int surplus = 0, creation = 0;
        double probability = 0.0;
        double probabilityFactor [] = {0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0}; //10 elements
        List<String> result = new ArrayList();
        if (relations == null ) throw new IllegalArgumentException("Nodes is Null");
        if (article == null ) throw new IllegalArgumentException("Article is Null");
        for (Relationship r : relations){
            if (!r.getAllProperties().keySet().contains("typeReportRelation") || ("".equals(r.getProperty("typeReportRelation").toString()))){                
                result.add("error: Subgraph relations without typeReportRelation");
                return result;
            }
            
            if ("necessary".equals(r.getProperty("typeReportRelation").toString())){
                //log.info(r.getProperty("typeReportRelation").toString() + ": " + r.getProperty("factor").toString());
                int probabilityElement = Integer.parseInt(r.getProperty("probabilty_element").toString());
                necessary.add(r.getProperty("probabilty_element").toString());
                double factor = Double.parseDouble(r.getProperty("factor").toString());
                probabilityFactor [probabilityElement] = probabilityFactor [probabilityElement] + factor;                
            }
            if ("surplus".equals(r.getProperty("typeReportRelation").toString())){
                //log.info(r.getProperty("typeReportRelation").toString() + ": ");
                surplus++;                
            }
            if ("created".equals(r.getProperty("typeReportRelation").toString())){
                //log.info(r.getProperty("typeReportRelation").toString() + ": ");
                creation++;                
            } else {
                //log.info(r.getProperty("typeReportRelation").toString() + ": ");
            }
            
            if (r.getStartNode().getAllProperties().keySet().contains("TheftPerpretator")){
                TheftPerpretator  = getQualifiedRelationship(r.getStartNode(), "TheftPerpretator");
                Stolengoods  = getQualifiedRelationship(r.getStartNode(), "Stolengoods");
                BurglaryCrime  = getQualifiedRelationship(r.getStartNode(), "BurglaryCrime");
                HouseOrPremiseBreaking  = getQualifiedRelationship(r.getStartNode(), "HouseOrPremiseBreaking");
                RobberyWithIntimidationOrViolence  = getQualifiedRelationship(r.getStartNode(), "RobberyWithIntimidationOrViolence");
            }
        }
        
        for (int x=0; x < probabilityFactor.length; x++) {            
            probability = probability +  probabilityFactor[x] / (necessary.size() + creation);
            //log.info(x+1 + "element: " + probability );
        }
        log.info("total element: " + probability );
        log.info("creation: " + creation );
        log.info("surplus: " + surplus );
        log.info("necessary: " + necessary.size() );
        log.info( "final factor: " + (necessary.size() + creation) / (necessary.size() + creation + surplus) );
        probability = probability * (necessary.size() + creation) / (necessary.size() + creation + surplus);
        result.add(Double.toString(probability));
        if (!"".equals(TheftPerpretator)) result.add("TheftPerpretator: " + TheftPerpretator);
        if (!"".equals(Stolengoods)) result.add("Stolengoods: " + Stolengoods);
        if (!"".equals(BurglaryCrime)) result.add("BurglaryCrime: " + BurglaryCrime);
        if (!"".equals(HouseOrPremiseBreaking)) result.add("HouseOrPremiseBreaking: " + HouseOrPremiseBreaking);
        if (!"".equals(RobberyWithIntimidationOrViolence)) result.add("RobberyWithIntimidationOrViolence: " + RobberyWithIntimidationOrViolence);
        return result;
    }
    
    private String getQualifiedRelationship(Node n, String property){  
        if (n.getAllProperties().keySet().contains(property)){
            return n.getProperty(property).toString();
        }
        return "";
    }
    
    
    public enum OrClauseArticle241_4 { 
                    ns0__AggravatingFactorAffectingInjuredParty, 
                    ns0__AggravatyFactorAffectsAccusedParty, 
                    ns0__AgriculturalOrLivestockProduct, 
                    ns0__ArtisticThing, 
                    ns0__CulturalThing, 
                    ns0__EssentialThing, 
                    ns0__HistoricalThing, 
                    ns0__ProvisionOfServiceThing, 
                    ns0__ScientificThing
    }
    
    public enum OrClauseArticle240_2 { 
                    AgriculturalOrLivestockProduct,
                    ArtisticThing,
                    CulturalThing,
                    EssentialThing,
                    HistoricalThing,
                    ProvisionOfServiceThing,
                    ScientificThing
    }
    
    public enum OrClauseArticle235_1__1 { 
                    ThingCharacteristic
    }
    
    public enum OrClauseArticle235_1__2 { 
                    AggravatingFactorAffectingInjuredParty,
    }
    
    public enum OrClauseArticle235_2 {
                    AgriculturalOrLivestockProduct, 
                    ArtisticThing, 
                    CulturalThing, 
                    EssentialThing, 
                    HistoricalThing, 
                    ProvisionOfServiceThing, 
                    ScientificThing
    }
    
    public void setNotConsideredIncomingRelation(Node n) {
        n.getRelationships(Direction.INCOMING).iterator()
                    .forEachRemaining(rel -> { 
                        setIncomingTypeReportRelation(rel, "not_considered");
                    });
    }
    
    public void setNotConsideredRelation(Node n, String relationType) {
        n.getRelationships(Direction.OUTGOING).iterator()
                    .forEachRemaining(rel -> { 
                        if (rel.getType().toString().equals(relationType)) {
                            setIncomingTypeReportRelation(rel, "not_considered");
                        }
                    });
    }
    
    public LinkedHashSet<Relationship> findSomeRelationTypeAndObjectValueCostMinus400(Node n, 
                                    String relationType, 
                                    String nodeLabel, 
                                    LinkedHashSet<Relationship> relation) {
        LinkedHashSet<Relationship> rlist = new LinkedHashSet<>();
//        n.getRelationships(Direction.OUTGOING).iterator()
         n.getRelationships(Direction.OUTGOING).iterator()
                    .forEachRemaining(rel -> 
                            addRelationsWithObjectValueCost(rlist, rel, relationType, nodeLabel));
//        setNotConsideredIncomingRelation(n);
        
        //Create Object-node and relation if not exists  
        if (rlist.size()< 1){
            //log.info("\tCreate node with relationType:" + relationType);
            Node o = tx.createNode(Label.label(nodeLabel));
            o.setProperty("name", "no_name");
            o.setProperty("ns0__ValueCost",Double.toString(1.0));
            Relationship r = n.createRelationshipTo(o, RelationshipType.withName(relationType));
            setTypeReportRelation(r, "created");
            rlist.add(r);
        }
        //change the relationship rate according to the sum of costs
        else {
            double sumValueCost = 0.0;
            for (Relationship r : rlist) {
                sumValueCost = sumValueCost + Double.parseDouble(r.getEndNode().getProperty("ns0__ValueCost").toString());
            }
            if (!(sumValueCost < 400.0)) {
                for (Relationship r : rlist) {
                    setNullProbabilityElementAndFactor(r);
                    r.setProperty("typeReportRelation", "surplus");
                }
                //log.info("\tCreate node with relationType:" + relationType);
                Node o = tx.createNode(Label.label(nodeLabel));
                o.setProperty("name", "no_name");
                Relationship r = n.createRelationshipTo(o, RelationshipType.withName(relationType));
                setTypeReportRelation(r, "created");
                o.setProperty("ns0__ValueCost",Double.toString(1.0));
                rlist.add(r);
                //relation.add(r);
            }
        
                
        }   
        return rlist;
    }
    
    public LinkedHashSet<Relationship> findSomeRelationTypeAndObjectValueCostOver400(Node n, 
                                    String relationType, 
                                    String nodeLabel, 
                                    LinkedHashSet<Relationship> relation) {
        LinkedHashSet<Relationship> rlist = new LinkedHashSet<>();
         n.getRelationships(Direction.OUTGOING).iterator()
                    .forEachRemaining(rel -> 
                            addRelationsWithObjectValueCost(rlist, rel, relationType, nodeLabel));
//        setNotConsideredIncomingRelation(n);
        
        //Create Object-node and relation if not exists  
        if (rlist.size()< 1){
            //log.info("\tCreate node with relationType:" + relationType);
            Node o = tx.createNode(Label.label(nodeLabel));
            o.setProperty("name", "no_name");
            Relationship r = n.createRelationshipTo(o, RelationshipType.withName(relationType));
            setTypeReportRelation(r, "created");
            o.setProperty("ns0__ValueCost",Double.toString(401.00));
            rlist.add(r);
        }
        else {
            double sumValueCost = 0.0;
            for (Relationship r : rlist) {
                sumValueCost = sumValueCost + Double.parseDouble(r.getEndNode().getProperty("ns0__ValueCost").toString());
            }
            if (!(sumValueCost >= 400.0))  {
                for (Relationship r : rlist) {
                    setNullProbabilityElementAndFactor(r);
                    r.setProperty("typeReportRelation", "surplus");
                }
                //log.info("\tCreate node with relationType:" + relationType);
                Node o = tx.createNode(Label.label(nodeLabel));
                o.setProperty("name", "no_name");
                Relationship r = n.createRelationshipTo(o, RelationshipType.withName(relationType));
                setTypeReportRelation(r, "created");
                o.setProperty("ns0__ValueCost",Double.toString(401.00));
                rlist.add(r);
                //relation.add(r);
            }
        
                
        }   
        return rlist;
    }
    
    public LinkedHashSet<Relationship> checkSomeRelationTypeAndObject(Node n, 
                                    String relationType, 
                                    String nodeLabel, 
                                    LinkedHashSet<Relationship> relation) {
        LinkedHashSet<Relationship> rlist = new LinkedHashSet<>();
        n.getRelationships(Direction.OUTGOING).iterator()
                    .forEachRemaining(rel -> 
                            addRelations(rlist, rel, relationType, nodeLabel));
        setNotConsideredIncomingRelation(n);
        
        //Create Object-node and relation if not exists  
        if (rlist.size()< 1){
            log.info("\tCreate node with relationType:" + relationType);
                Node o = tx.createNode(Label.label(nodeLabel));
                o.setProperty("name", "no_name");                
                Relationship r = n.createRelationshipTo(o, RelationshipType.withName(relationType));
                setTypeReportRelation(r, "created");
                rlist.add(r);
                //relation.add(r);
        }
        log.info("\tcheckSomeRelation " + relationType + ": " + rlist.size());
        return rlist;
    }
    
    
    public LinkedHashSet<Relationship> checkSomeRelationTypeAndObjectWithoutCreation(Node n, 
                                    String relationType, 
                                    String nodeLabel, 
                                    LinkedHashSet<Relationship> relation) {
        LinkedHashSet<Relationship> rlist = new LinkedHashSet<>();
        n.getRelationships(Direction.OUTGOING).iterator()
                    .forEachRemaining(rel -> 
                            addRelations(rlist, rel, relationType, nodeLabel));
        setNotConsideredIncomingRelation(n);
        return rlist;
    }
    
    public LinkedHashSet<Relationship> findSomeRelationTypeAndObject(Node n, 
                                    String relationType, 
                                    String nodeLabel, 
                                    LinkedHashSet<Relationship> relation) {
        LinkedHashSet<Relationship> rlist = new LinkedHashSet<>();
        n.getRelationships(Direction.OUTGOING).iterator()
                    .forEachRemaining(rel -> 
                            addRelationsSimple(rlist, rel, relationType, nodeLabel));
        
//        //Create Object-node and relation if not exists  
//        if (rlist.size()< 1){
//            //log.info("\tCreate node with relationType:" + relationType);
//                Node o = tx.createNode(Label.label(nodeLabel));
//                o.setProperty("name", "no_name");                
//                Relationship r = n.createRelationshipTo(o, RelationshipType.withName(relationType));
//                setTypeReportRelation(r, "created");
//                rlist.add(r);
//                //relation.add(r);
//        }
        return rlist;
    }
    
    public LinkedHashSet<Relationship> checkNotSomeRelationTypeAndObject(Node n, 
                                    String relationType, 
                                    String nodeLabel, 
                                    LinkedHashSet<Relationship> relation) {
        LinkedHashSet<Relationship> rlist = new LinkedHashSet<>();
        n.getRelationships(Direction.OUTGOING).iterator()
                    .forEachRemaining(rel -> 
                            addNegationRelations(rlist, rel, relationType, nodeLabel));
        setNotConsideredIncomingRelation(n);
        return rlist;
    }
    
    public LinkedHashSet<Relationship> checkOrRelationTypeAndListObject(Node n, 
                                    String relationType, 
                                    List<String> listLabel,  
                                    LinkedHashSet<Relationship> relation) {
        LinkedHashSet<Relationship> rlist = new LinkedHashSet<>();
        n.getRelationships(Direction.OUTGOING).iterator()
                    .forEachRemaining(rel -> {
                                addRelationsListLabel(rlist, rel, relationType, listLabel);
                            });
        setNotConsideredIncomingRelation(n);
        //Create Object-node and relation if not exists  
        if (rlist.size()< 1){
            //log.info("\tCreate node with relationType:" + relationType);
            Node o = tx.createNode(Label.label(listLabel.get(0)));
            o.setProperty("name", "no_name");
            Relationship r = n.createRelationshipTo(o, RelationshipType.withName(relationType));
            setTypeReportRelation(r, "created_or");
            rlist.add(r);
            //relation.add(r);
        }   
        return rlist;
    }
    
    public LinkedHashSet<Relationship> checkOrRelationTypeAndListObjectWithoutCreate(Node n, 
                                    String relationType, 
                                    List<String> listLabel,  
                                    LinkedHashSet<Relationship> relation) {
        LinkedHashSet<Relationship> rlist = new LinkedHashSet<>();
        n.getRelationships(Direction.OUTGOING).iterator()
                    .forEachRemaining(rel -> {
                                addRelationsListLabel(rlist, rel, relationType, listLabel);
                            });
        setNotConsideredIncomingRelation(n); 
        return rlist;
    }
    
  
    private  void addRelationsSimple(LinkedHashSet<Relationship> list, Relationship relationship, String relationType, String nodeLabel){
        if (relationship.getType().name().startsWith(relationType))
            relationship.getEndNode().getLabels().forEach(label-> addRelationsByObjectSimple(list, relationship, label, relationType, nodeLabel));             
        
    }
    
    
    private  void addRelations(LinkedHashSet<Relationship> list, Relationship relationship, String relationType, String nodeLabel){
        if (relationship.getType().name().startsWith(relationType))
            relationship.getEndNode().getLabels().forEach(label-> addRelationsByObject(list, relationship, label, relationType, nodeLabel));             
        else
           setTypeReportRelation(relationship, "surplus"); 
    }
    
    private  void addRelationsWithObjectValueCost(LinkedHashSet<Relationship> list, Relationship relationship, String relationType, String nodeLabel){
        if (relationship.getType().name().startsWith(relationType))
            relationship.getEndNode().getLabels().forEach(label-> addRelationsByObjectValueCost(list, relationship, label, relationType, nodeLabel));             
        else
           setTypeReportRelation(relationship, "surplus"); 
    }
    
  
    
    private  void addNegationRelations(LinkedHashSet<Relationship> list, Relationship relationship, String relationType, String nodeLabel){
        if (relationship.getType().name().startsWith(relationType))
            relationship.getEndNode().getLabels().forEach(label-> addNegationRelationsByObject(list, relationship, label, relationType, nodeLabel));             
        else
           setTypeReportRelation(relationship, "surplus"); 
    }
    
    
    
    private  void addRelationsListLabel(LinkedHashSet<Relationship> list, Relationship relationship, String relationType, List<String> listLabel){
        if (relationship.getType().name().startsWith(relationType))
            relationship.getEndNode().getLabels().forEach(label->
                        addRelationsByListObject(list, relationship, label, relationType, listLabel)); 
        else 
            setTypeReportRelation(relationship, "surplus");
    }

    private  void addRelationsByObjectValueCost(LinkedHashSet<Relationship> list,  Relationship relationship, Label label, String relationType, String nodeLabel) {
        //log.info( "addRelationsByObject: "+ relationType);
        if (label.name().equals(nodeLabel) 
                && relationship.getEndNode().getAllProperties().keySet().contains("ns0__ValueCost")){
            list.add(relationship);
            setTypeReportRelation(relationship, "necessary");
        } else
            setTypeReportRelation(relationship, "surplus");
    }  

      
    private  void addRelationsByObject(LinkedHashSet<Relationship> list,  Relationship relationship, Label label, String relationType, String nodeLabel) {
        //log.info( "addRelationsByObject: "+ relationType);
        if (label.name().equals(nodeLabel)){
            list.add(relationship);
            setTypeReportRelation(relationship, "necessary");
        } else
            setTypeReportRelation(relationship, "surplus");
    }
    
     private  void addRelationsByObjectSimple(LinkedHashSet<Relationship> list,  Relationship relationship, Label label, String relationType, String nodeLabel) {
        //log.info( "addRelationsByObject: "+ relationType);        
        if (label.name().equals(nodeLabel))
            list.add(relationship);            
    }
    
    private  void addNegationRelationsByObject(LinkedHashSet<Relationship> list,  Relationship relationship, Label label, String relationType, String nodeLabel) {
        //log.info( "addNegationRelationsByObject: "+ relationType);
        if (label.name().equals(nodeLabel)){
            list.add(relationship);
//            setTypeReportRelation(relationship, "negation");
            setTypeReportRelation(relationship, "surplus");
        } 
//        else
//            setTypeReportRelation(relationship, "surplus");
    }
    
    private void setIncomingTypeReportRelation(Relationship r, String type) {   
//        //log.info("typeReportRelation: " +  r.getAllProperties().keySet().contains("typeReportRelation"));
        if (!r.getAllProperties().keySet().contains("typeReportRelation") || 
                "".equals(r.getProperty("typeReportRelation").toString()) ||
                "surplus".equals(r.getProperty("typeReportRelation").toString()))
            r.setProperty("typeReportRelation", type);        
    }
    
    private void setTypeReportRelation(Relationship r, String type) {   
//        log.info("typeReportRelation: " +  r.getAllProperties().keySet().contains("typeReportRelation"));
        if (!r.getAllProperties().keySet().contains("typeReportRelation") || ("".equals(r.getProperty("typeReportRelation").toString())))
            r.setProperty("typeReportRelation", type);
        else if ("surplus".equals(r.getProperty("typeReportRelation").toString())) 
            r.setProperty("typeReportRelation", type);
//        log.info("typeReportRelation: " +  r.getProperty("typeReportRelation").toString());
    }
    
    //TheftPerpretator - StolenGoods -
    private void setQualifiedRelationship(Node n, Relationship r, String property){  
        if (r.getAllProperties().keySet().contains("typeReportRelation")){
            log.info("Qualified property of " + r.getType().name() + ": " + r.getProperty("typeReportRelation").toString());
            switch (r.getProperty("typeReportRelation").toString()){
                case "created":
                    n.setProperty(property, "Unknown");
                    break;
                case "necessary":
                    n.setProperty(property, "Known");
                    break;
            }
        }         
    }
    
    
    private  void addRelationsByListObject(LinkedHashSet<Relationship> list,  Relationship relationship, Label label, String relationType, List<String> listLabel) {
        
        listLabel.forEach(nodeLabel -> {
            if (label.name().equals(nodeLabel)){
                list.add(relationship);
                setTypeReportRelation(relationship, "necessary_or");
            } else
                setTypeReportRelation(relationship, "surplus");
        }); 
    }
    
    
//    public  double numRelationOfArticle(String rootArticle){   
//        //log.info("numRelationOfArticle key: " + rootArticle);
//        switch (rootArticle) {
//            case "Report" :
//                return 0;                                //revised
//            case "PropertyCrimeReport" :
//                return 2;                                //revised
//            case "Theft" :
//                return 3;                                //revised
//            case "Robbery" :
//                return 4;                                //revised
//            case "TheftByOwner" :
//                return 5;                                //revised
//            case "TheftByNotOwner" :
//               return 5;                                 //revised
//            case "Article240" :
//                return 7;
//            case "Article241" :
//                return 7;
//            case "Article242" : 
//                //log.info("numRelationOfArticle : 4");
//                return 4;                           //revised
//            case "Article234_1" :
//                return 5;                           //revised
//            case "Article234_2" :
//                return 5;                           //revised
//            case "Article234_3" :
//                return 6;                           //revised
//            case "Article235_1" :
//                return 10000;
//            case "Article235_2" :
//                return 9;
//            case "Article236_1" :
//                return 9;
//            case "Article236_2" :
//                return 9;
//            case "Article240_2" :
//                return 8;
//            case "Article241_4" :
//                return 100000;
//            case "Article242_2" :
//                return 8;
//            case "Article242_3" :
//                return 9;
//            case "Article242_4" :
//                return 9;
//        }
//        return 0;
//    }
    
    public void setProbabilityElementAndFactor (LinkedHashSet<Relationship> relations, 
            int probabilityElement, 
            double factor){
        for (Relationship r : relations){
            r.setProperty("probabilty_element", String.valueOf(probabilityElement));
            r.setProperty("factor", String.valueOf(factor));
            log.info("\tProb from " +r.getStartNode().getProperty("name").toString() + " --- " + r.getType().name() + ": " + factor
                        + " ---> " + r.getEndNode().getProperty("name").toString());
        }
            
    }
    
    public void setProbabilityElementFactorAndTypeRel (LinkedHashSet<Relationship> relations, 
            int probabilityElement, 
            double factor,
            String typeRel){
        for (Relationship r : relations){
            r.setProperty("probabilty_element", String.valueOf(probabilityElement));
            r.setProperty("factor", String.valueOf(factor));
            log.info("\tProb from " +r.getStartNode().getProperty("name").toString() + " --- " + r.getType().name() + ": " + factor
                        + " ---> " + r.getEndNode().getProperty("name").toString());
            setTypeReportRelation(r, typeRel);
        }
            
    }
    

    
    public void setNullProbabilityElementAndFactor (Relationship r){
        r.setProperty("probabilty_element", "");
        r.setProperty("factor", "");
    
    }
    
    public double getFactor (Relationship r) {
        double result;
        if (!r.getAllProperties().keySet().contains("factor") || ("".equals(r.getProperty("factor").toString())))
            result = 1.0;
        else
            result = Double.parseDouble(r.getProperty("factor").toString());
        log.info("\tInitialFactor: " + result);
        return result;
    }
    
    public void assignSurplusRelationInGraph(Node n) {
        n.getRelationships().iterator()
                    .forEachRemaining(rel -> { 
                        if (!rel.getAllProperties().keySet().contains("typeReportRelation")) {
                            if (!rel.getType().name().equals("ns0__isEmployed"))
                                setTypeReportRelation(rel, "surplus");
                            else
                                setTypeReportRelation(rel, "not_considered");
                            assignSurplusRelationInGraph(rel.getEndNode());
                         }
                    });
    }        
    
 
    
    
    public  void defineArticlePriorProbability(Node n, 
                                            String article, 
                                            String rootArticle, 
                                            LinkedHashSet<Relationship> relation){
//        double baseRate = 1.0/numRelationOfArticle(rootArticle);
//        log.info("defineArticlePriorProbability " + rootArticle + " in "+ article);
        switch (article) {
            case "Report" :
                log.info("Surplus: " + rootArticle);
                //Poner todas las relaciones del grafo a surplus
                assignSurplusRelationInGraph(n);
                log.info("Report: " + rootArticle);
                break;
            case "PropertyCrimeReport" :
                defineArticlePriorProbability(n, "Report", rootArticle, relation);
                log.info("PropertyCrimeReport");
                LinkedHashSet<Relationship> stolenthing  = checkSomeRelationTypeAndObject(n, 
                                                                    "ns0__stolenthing", 
                                                                    "ns0__StolenGoods",
                                                                     relation);
                setProbabilityElementAndFactor (stolenthing, 1, 1.0/stolenthing.size());
                relation.addAll(stolenthing);
                //log.info("\tstolenthing relations: " + stolenthing.size());
                for (Relationship r : stolenthing) {
                    setNotConsideredRelation(r.getEndNode(), "ns0__usedBy");
                    LinkedHashSet<Relationship> belongsTo  = checkSomeRelationTypeAndObject(r.getEndNode(), 
                                                            "ns0__belongsTo", 
                                                            "ns0__Person",
                                                             relation);
                    //log.info("\t\tstolenBy relations: " + belongsTo.size());
                    setProbabilityElementAndFactor (belongsTo, 2, getFactor(r) * 1.0/belongsTo.size());
                    this.setQualifiedRelationship(n, r, "Stolengoods");
                    relation.addAll(belongsTo);
                    
                }

                break;
            case "Theft" :
                defineArticlePriorProbability(n, "PropertyCrimeReport", rootArticle, relation);
                log.info("Theft");

                LinkedHashSet<Relationship> notHasOffenceCharacteristic  = checkNotSomeRelationTypeAndObject(n, 
                                                                    "ns0__hasOffenceCharacteristic", 
                                                                    "ns0__RobberyCharacteristic",
                                                                     relation);

                relation.addAll(notHasOffenceCharacteristic);

                //log.info("\thasOffenceCharacteristic relations: " + notHasOffenceCharacteristic.size());
                LinkedHashSet<Relationship> stolenthing2  = findSomeRelationTypeAndObject(n, 
                                                                    "ns0__stolenthing", 
                                                                    "ns0__StolenGoods",
                                                                     relation);
//                relation.addAll(stolenthing2);
                //log.info("\tstolenthing relations: " + stolenthing2.size());
                for (Relationship r : stolenthing2) {
                    LinkedHashSet<Relationship> stolenBy  = checkSomeRelationTypeAndObject(r.getEndNode(), 
                                                            "ns0__stolenBy", 
                                                            "ns0__Person",
                                                             relation);
//                    for (Relationship r2 : stolenBy) { //Solo para el casode los acusados no tratados
//                        setNotConsideredIncomingRelation(r2.getEndNode());
//                        r2.getEndNode().getRelationships(Direction.OUTGOING).iterator()
//                                .forEachRemaining(rel -> setTypeReportRelation(rel, "surplus"));
//                    }
                    setProbabilityElementAndFactor (stolenBy, 3, getFactor(r) * 1.0/stolenBy.size());
                    this.setQualifiedRelationship(n, r, "TheftPerpretator");
                    relation.addAll(stolenBy);
                    //log.info("\t\tstolenBy relations: " + stolenBy.size());
                }
                break;
            case "Robbery" :
                defineArticlePriorProbability(n, "PropertyCrimeReport", rootArticle, relation);
                log.info("Robbery");
                LinkedHashSet<Relationship> hasOffenceCharacteristic  = checkSomeRelationTypeAndObject(n, 
                                                                    "ns0__hasOffenceCharacteristic", 
                                                                    "ns0__RobberyCharacteristic",
                                                                     relation);
                setProbabilityElementAndFactor (hasOffenceCharacteristic, 4, 1.0/hasOffenceCharacteristic.size());
                relation.addAll(hasOffenceCharacteristic);
                //log.info("\thasOffenceCharacteristic relations: " + hasOffenceCharacteristic.size());
                LinkedHashSet<Relationship> stolenthing1  = findSomeRelationTypeAndObject(n, 
                                                                    "ns0__stolenthing", 
                                                                    "ns0__StolenGoods",
                                                                     relation);
                //log.info("\tstolenthing relations: " + stolenthing1.size());
                for (Relationship r : stolenthing1) {
                    LinkedHashSet<Relationship> stolenBy  = checkSomeRelationTypeAndObject(r.getEndNode(), 
                                                            "ns0__stolenBy", 
                                                            "ns0__Person",
                                                             relation);
                    //Evitar surplus
                    setNotConsideredRelation(r.getEndNode(), "ns0__usedByOwner");
                    setNotConsideredRelation(r.getEndNode(), "ns0__stolenByOwner");
                    
                    setProbabilityElementAndFactor (stolenBy, 3, getFactor(r) * 1.0/stolenBy.size());
                    this.setQualifiedRelationship(n, r, "TheftPerpretator");
                    relation.addAll(stolenBy);
                    //log.info("\t\tstolenBy relations: " + stolenBy.size());
                }

                break;
            case "TheftByOwner" :
                defineArticlePriorProbability(n, "Theft", rootArticle, relation);
                log.info("TheftByOwner");
                LinkedHashSet<Relationship> stolenthing3  = findSomeRelationTypeAndObject(n, 
                                                                    "ns0__stolenthing", 
                                                                    "ns0__StolenGoods",
                                                                     relation);
                //log.info("\tstolenthing relations: " + stolenthing3.size());
                for (Relationship r : stolenthing3) {
                    LinkedHashSet<Relationship> stolenByOwner   = checkSomeRelationTypeAndObject(r.getEndNode(), 
                                                            "ns0__stolenByOwner", 
                                                            "ns0__Person",
                                                             relation);
//                    setProbabilityElementAndFactor (stolenByOwner, 5, getFactor(r) * 1.0/stolenByOwner.size());
                    setProbabilityElementAndFactor (stolenByOwner, 5, getFactor(r) * 1.0/stolenByOwner.size());
                    relation.addAll(stolenByOwner);
                    //log.info("\t\tusedByOwner relations: " + stolenByOwner .size());
                }
                break;
            case "TheftByNotOwner" :
                defineArticlePriorProbability(n, "Theft", rootArticle, relation);
                log.info("TheftByNotOwner");
                LinkedHashSet<Relationship> stolenthing4  = findSomeRelationTypeAndObject(n, 
                                                                    "ns0__stolenthing", 
                                                                    "ns0__StolenGoods",
                                                                     relation);
                //log.info("\tstolenthing relations: " + stolenthing4.size());
                for (Relationship r : stolenthing4) {                    
                    LinkedHashSet<Relationship> usedByOwner   = checkSomeRelationTypeAndObject(r.getEndNode(), 
                                                            "ns0__usedByOwner", 
                                                            "ns0__Person",
                                                             relation);
                    setProbabilityElementAndFactor (usedByOwner, 6, getFactor(r) * 1.0/usedByOwner.size());
                    relation.addAll(usedByOwner);
                    //log.info("\t\tusedByOwner relations: " + usedByOwner.size());
                }
                break;
            case "Article240_1" :
                 defineArticlePriorProbability(n, "Robbery", rootArticle, relation);
                log.info("Article240_1");
                LinkedHashSet<Relationship> someHasOffenceCharacteristic_1 = checkSomeRelationTypeAndObject(n, 
                                                                    "ns0__hasOffenceCharacteristic", 
                                                                    "ns0__BurglaryCrime",
                                                                     relation);
                //No hace falta, ya está establecido en Robbery, sólo necesitamos crear si no existe 
//                setProbabilityElementAndFactor (someHasOffenceCharacteristic_1, 4, 1.0/someHasOffenceCharacteristic_1.size());
                for (Relationship r : someHasOffenceCharacteristic_1 ) {
                    this.setQualifiedRelationship(n, r, "BurglaryCrime");
                }
                relation.addAll(someHasOffenceCharacteristic_1);
                //log.info("\tsome hasOffenceCharacteristic relations: " + someHasOffenceCharacteristic_1.size());
                break;
            case "Article241" :
                defineArticlePriorProbability(n, "Robbery", rootArticle, relation);
                log.info("Article241");
                LinkedHashSet<Relationship> someHasOffenceCharacteristic_2 = checkSomeRelationTypeAndObject(n, 
                                                                    "ns0__hasOffenceCharacteristic", 
                                                                    "ns0__HouseOrPremiseBreaking",
                                                                     relation);
                for (Relationship r : someHasOffenceCharacteristic_2) {
                    this.setQualifiedRelationship(n, r, "HouseOrPremiseBreaking");
                }
                setProbabilityElementAndFactor (someHasOffenceCharacteristic_2, 4, 1.0/someHasOffenceCharacteristic_2.size());
                relation.addAll(someHasOffenceCharacteristic_2);
                //log.info("\tsome hasOffenceCharacteristic relations: " + someHasOffenceCharacteristic_2.size());
                break;
            case "Article242" : //7 relaciones y
            case "Article242_1" :
                defineArticlePriorProbability(n, "Robbery", rootArticle, relation);
                log.info("Article242--Article242_1");
                LinkedHashSet<Relationship> someHasOffenceCharacteristic_3 = checkSomeRelationTypeAndObject(n, 
                                                                    "ns0__hasOffenceCharacteristic", 
                                                                    "ns0__RobberyWithIntimidationOrViolence",
                                                                     relation);
                //No hace falta, ya está establecido en Robbery, sólo necesitamos crear si no existe 
//                setProbabilityElementAndFactor (someHasOffenceCharacteristic_3, 4, 1.0/someHasOffenceCharacteristic_3.size());
                for (Relationship r : someHasOffenceCharacteristic_3) {
                    this.setQualifiedRelationship(n, r, "RobberyWithIntimidationOrViolence");
                }
                relation.addAll(someHasOffenceCharacteristic_3);
                //log.info("\tsomeHasOffenceCharacteristic relations: " + someHasOffenceCharacteristic_3.size());                
                break;            
            case "Article234_1" :
                defineArticlePriorProbability(n, "TheftByNotOwner", rootArticle, relation);
                log.info("Article234_1");
                LinkedHashSet<Relationship> stolenthing6  = findSomeRelationTypeAndObject(n, 
                                                                    "ns0__stolenthing", 
                                                                    "ns0__StolenGoods",
                                                                     relation);
                LinkedHashSet<Relationship> valueCostOver400   = findSomeRelationTypeAndObjectValueCostOver400(n, 
                                                        "ns0__stolenthing", 
                                                        "ns0__StolenGoods",
                                                         stolenthing6);
                if(!valueCostOver400.isEmpty() && valueCostOver400.size()==1) {
                    setProbabilityElementAndFactor (valueCostOver400, 1, 1.0/valueCostOver400.size());
                    relation.addAll(valueCostOver400);
                }
                log.info("\t\tvalueCostOver400 movablethings: " + valueCostOver400.size());
                break;
            case "Article234_2" :
                defineArticlePriorProbability(n, "TheftByNotOwner", rootArticle, relation);
                log.info("Article234_2");
                LinkedHashSet<Relationship> stolenthing5  = findSomeRelationTypeAndObject(n, 
                                                                    "ns0__stolenthing", 
                                                                    "ns0__StolenGoods",
                                                                     relation);
                //log.info("\tstolenthing relations: " + stolenthing5.size());

                LinkedHashSet<Relationship> valueCostMinus400   = findSomeRelationTypeAndObjectValueCostMinus400(n, 
                                                        "ns0__stolenthing", 
                                                        "ns0__StolenGoods",
                                                         stolenthing5);
                if(!valueCostMinus400.isEmpty() && valueCostMinus400.size()==1) {
                    setProbabilityElementAndFactor (valueCostMinus400, 1, 1.0/valueCostMinus400.size());
                    relation.addAll(valueCostMinus400);
                }
                log.info("\t\tvalueCostMinus400 movablethings: " + valueCostMinus400.size());

                break;
            case "Article234_3" :
                defineArticlePriorProbability(n, "TheftByNotOwner", rootArticle, relation);
                log.info("Article234_3");
                LinkedHashSet<Relationship> hasOffenceCharacteristic_4  = checkSomeRelationTypeAndObject(n, 
                                                                    "ns0__hasOffenceCharacteristic", 
                                                                    "ns0__UnlawfulEntry",
                                                                     relation);
                setProbabilityElementAndFactor (hasOffenceCharacteristic_4, 4, 1.0/hasOffenceCharacteristic_4.size());
                relation.addAll(hasOffenceCharacteristic_4);
                //log.info("\thasOffenceCharacteristic relations: " + hasOffenceCharacteristic_4.size());                
                break;
            case "Article235_1" :
                defineArticlePriorProbability(n, "TheftByNotOwner", rootArticle, relation);
                log.info("Article235_1");
                article235Based(n, article, relation,true);
                break;
            case "Article235_2" :
                defineArticlePriorProbability(n, "TheftByNotOwner", rootArticle, relation);
                log.info("Article235_2");
                article235Based(n, article, relation, true);
                break;

            case "Article236_1":
                defineArticlePriorProbability(n, "TheftByOwner", rootArticle, relation);
                log.info("Article236_1");
                LinkedHashSet<Relationship> stolenthing8  = findSomeRelationTypeAndObject(n, 
                                                                    "ns0__stolenthing", 
                                                                    "ns0__StolenGoods",
                                                                     relation);
                //log.info("\tstolenthing relations: " + stolenthing8.size());
                LinkedHashSet<Relationship> valueCostMinus400_2   = findSomeRelationTypeAndObjectValueCostMinus400(n, 
                                                        "ns0__stolenthing", 
                                                        "ns0__StolenGoods",
                                                         stolenthing8);
                if(!valueCostMinus400_2.isEmpty() && valueCostMinus400_2.size()==1) {
                    setProbabilityElementAndFactor (valueCostMinus400_2, 1, 1.0/valueCostMinus400_2.size());
                    relation.addAll(valueCostMinus400_2);
                }
                //log.info("\t\tvalueCostMinus400 movablethings: " + valueCostMinus400_2.size());
                break;
            case "Article236_2" :
                defineArticlePriorProbability(n, "TheftByOwner", rootArticle, relation);
                log.info("Article236_2");
                LinkedHashSet<Relationship> stolenthing9  = findSomeRelationTypeAndObject(n, 
                                                                    "ns0__stolenthing", 
                                                                    "ns0__StolenGoods",
                                                                     relation);
                //log.info("\tstolenthing relations: " + stolenthing9.size());
                LinkedHashSet<Relationship> valueCostOver400_2   = findSomeRelationTypeAndObjectValueCostOver400(n, 
                                                        "ns0__stolenthing", 
                                                        "ns0__StolenGoods",
                                                         stolenthing9);
                if(!valueCostOver400_2.isEmpty() && valueCostOver400_2.size()==1) {
                    setProbabilityElementAndFactor (valueCostOver400_2, 1, 1.0/valueCostOver400_2.size());
                    relation.addAll(valueCostOver400_2);
                }
                //log.info("\t\tvalueCostMinus400 movablethings: " + valueCostOver400_2.size());
                break;
            case "Article240_2" : 
                defineArticlePriorProbability(n, "Article240_1", rootArticle, relation);
                log.info("Article240_2");
                article235Based(n, article, relation,true);
                break;
            case "Article241_1" :
                defineArticlePriorProbability(n, "Article241", rootArticle, relation);
                log.info("Article241_1");
                break;
            case "Article241_4" :
                defineArticlePriorProbability(n, "Article241", rootArticle, relation);
                log.info("Article241_4");
                LinkedHashSet<Relationship> someExistsOffenceAggravatingFactor = checkSomeRelationTypeAndObject(n, 
                                                                    "ns0__hasOffenceAggravatingFactor", 
                                                                    "ns0__DamageCaused",
                                                                     relation);
                //log.info("\tsomeHasOffenceCharacteristic relations: " + someExistsOffenceAggravatingFactor.size());
                if (!someExistsOffenceAggravatingFactor.isEmpty()) {
                    setProbabilityElementAndFactor (someExistsOffenceAggravatingFactor, 8, 1.0/someExistsOffenceAggravatingFactor.size());
                    relation.addAll(someExistsOffenceAggravatingFactor);
                    article235Based(n, article, relation, false);
                    break;
                }
                else 
                    article235Based(n, article, relation, true);
                    
//                LinkedHashSet<Relationship> article_241_4_clause = checkOrRelationTypeAndListObject(n, 
//                                                                    "ns0__stolenthing",
//                                                                    Stream.of(OrClauseArticle241_4.values())
//                                                                    .map(OrClauseArticle241_4::name)
//                                                                    .collect(Collectors.toList()),
//                                                                     relation);
//                //log.info("\tsomeHasOffenceCharacteristic relations: " + article_241_4_clause.size());
//                setProbabilityElementAndFactor (article_241_4_clause, 1, 1.0/article_241_4_clause.size());
//                relation.addAll(article_241_4_clause);

                break;
            case "Article242_2" :
                defineArticlePriorProbability(n, "Article242", rootArticle, relation);
                log.info("Article242_2");
                LinkedHashSet<Relationship> someHasOffenceCharacteristic1 = checkSomeRelationTypeAndObject(n, 
                                                                    "ns0__hasOffenceCharacteristic", 
                                                                    "ns0__HouseOrPremiseBreaking",
                                                                     relation);
                //log.info("\tsomeHasOffenceCharacteristic relations: " + someHasOffenceCharacteristic1.size());
                //No hace falta, ya está establecido en Robbery, sólo necesitamos crear si no existe
//                setProbabilityElementAndFactor (someHasOffenceCharacteristic1, 4, 1.0/someHasOffenceCharacteristic1.size());
                relation.addAll(someHasOffenceCharacteristic1);
                break;
            case "Article242_3" :
                defineArticlePriorProbability(n, "Article242", rootArticle, relation);
                log.info("Article242_3");
                LinkedHashSet<Relationship> hasAggravatingFactor = checkSomeRelationTypeAndObject(n, 
                                                                    "ns0__hasAggravatingFactor", 
                                                                    "ns0__ArmedRobbery",
                                                                     relation);
                //log.info("\tsome hasAggravatingFactor relations: " + hasAggravatingFactor.size());
                //No hace falta, ya está establecido en Robbery, sólo necesitamos crear si no existe
                setProbabilityElementAndFactor (hasAggravatingFactor , 9, 1.0/hasAggravatingFactor.size());
                relation.addAll(hasAggravatingFactor);
                break;
            case "Article242_4" :
                defineArticlePriorProbability(n, "Article242", rootArticle, relation);
                log.info("Article242_4");
                LinkedHashSet<Relationship> hasMitigatingFactor = checkSomeRelationTypeAndObject(n, 
                                                                    "ns0__hasMitigatingFactor", 
                                                                    "ns0__MinimalIntimidationOrViolence",
                                                                     relation);
                //log.info("\tsome hasMitigatingFactor relations: " + hasMitigatingFactor.size());
                setProbabilityElementAndFactor (hasMitigatingFactor , 10, 1.0/hasMitigatingFactor.size());
                relation.addAll(hasMitigatingFactor);
                break;
        }
 

    }
    
    public void article235Based( Node n,
                                 String article,
                                 LinkedHashSet<Relationship> relation,
                                 boolean creation){
        LinkedHashSet<Relationship> stolenthing7  = findSomeRelationTypeAndObject(n, 
                                                            "ns0__stolenthing", 
                                                            "ns0__StolenGoods",
                                                             relation);
        log.info("\tarticle235Based stolenthing relations: " + stolenthing7.size());
        LinkedHashSet<Relationship> hasThingCharacteristic = new LinkedHashSet<>();
        LinkedHashSet<Relationship> hasOffenceAggravatingFactor  = new LinkedHashSet<>();
        LinkedHashSet<Relationship> hasPreviusSentence1 = new LinkedHashSet<>();
        LinkedHashSet<Relationship> hasAccomplice1 = new LinkedHashSet<>();
        LinkedHashSet<Relationship> belongsToCriminalOrganization1 = new LinkedHashSet<>();
        for (var r : stolenthing7) {
            log.info("\t\tArticle235Based stolenthing" +r.getStartNode().getProperty("name").toString() + " --- " + r.getType().name() 
                    + " ---> " + r.getEndNode().getProperty("name").toString());
            LinkedHashSet<Relationship> htc = findSomeRelationTypeAndObject(r.getEndNode(), 
                                                            "ns0__hasThingCharacteristic", 
                                                            "ns0__ThingCharacteristic",
                                                             relation);
            hasThingCharacteristic.addAll(htc);
//                   checkOrRelationTypeAndListObjectWithoutCreate(r.getEndNode(), 
//                                                    "ns0__hasThingCharacteristic",
//                                                    Stream.of(OrClauseArticle235_1__1.values())
//                                                    .map(OrClauseArticle235_1__1::name)
//                                                    .collect(Collectors.toList()),
//                                                     relation);                 

            LinkedHashSet<Relationship> stolenBy7  = findSomeRelationTypeAndObject(r.getEndNode(), 
                                                            "ns0__stolenBy",
                                                            "ns0__Accused",
                                                             relation);
            log.info("\tarticle235Based stolenBy7 relations: " + stolenBy7.size());
            LinkedHashSet<Relationship> belongsTo7  = findSomeRelationTypeAndObject(r.getEndNode(), 
                                                            "ns0__belongsTo", 
                                                            "ns0__Victim",
                                                             relation);
            for (var r2 : stolenBy7) {
//                List<String> list = Arrays.asList("ns0__PunishentForCrimesAgainstProperty");
                log.info("\t\t\tArticle235Based stolenBy7" +r2.getStartNode().getProperty("name").toString() + " --- " + r2.getType().name() 
                                    + " ---> " + r2.getEndNode().getProperty("name").toString());
                LinkedHashSet<Relationship> hos  = findSomeRelationTypeAndObject(r2.getEndNode(), 
                                                            "ns0__hasPreviusSentence",                
                                                            "ns0__PropertyCrimePunishments",
                                                             relation);
                log.info("\t\t\tarticle235Based hos relations: " + hos.size());
                hasPreviusSentence1.addAll(hos);
//                        checkOrRelationTypeAndListObjectWithoutCreate
//                list = Arrays.asList("ns0__Person");
                LinkedHashSet<Relationship> ha  = findSomeRelationTypeAndObject(r2.getEndNode(), 
                                                            "ns0__hasAccomplice", 
                                                            "ns0__Person",
                                                             relation);
                hasAccomplice1.addAll(ha);
//                list = Arrays.asList("ns0__CriminalOrganization");
                LinkedHashSet<Relationship> bco  = findSomeRelationTypeAndObject(r2.getEndNode(), 
                                                            "ns0__belongsToCriminalOrganization", 
                                                            "ns0__CriminalOrganization",
                                                             relation);
                belongsToCriminalOrganization1.addAll(bco);
            }
            
            for (var r3 : belongsTo7) {
//                List<String> list = Arrays.asList("ns0__PunishentForCrimesAgainstProperty");
                LinkedHashSet<Relationship> eaf  = findSomeRelationTypeAndObject(r3.getEndNode(), 
                                                            "ns0__hasEffectOffence", 
                                                            "ns0__OffenceEffects",
                                                             relation);
                hasOffenceAggravatingFactor.addAll(eaf);
            }
        }
        
         
//        LinkedHashSet<Relationship> hasOffenceAggravatingFactor = checkOrRelationTypeAndListObjectWithoutCreate(n, 
//                                                            "ns0__hasOffenceAggravatingFactor",
//                                                            Stream.of(OrClauseArticle235_1__2.values())
//                                                            .map(OrClauseArticle235_1__2::name)
//                                                            .collect(Collectors.toList()),
//                                                             relation);                
        log.info("\thasOffenceAggravatingFactor relations: " + hasOffenceAggravatingFactor.size());
        log.info("\thasPreviusSentence1 relations: " + hasPreviusSentence1.size());
        log.info("\thasAccomplice1 relations: " + hasAccomplice1.size());
        log.info("\thasThingCharacteristic relations: " + hasThingCharacteristic.size());
        log.info("\tbelongsToCriminalOrganization1 relations: " + belongsToCriminalOrganization1.size());

        //Check conditions
        for (var os : hasPreviusSentence1){
            log.info("\t\tArticle235Based " +os.getStartNode().getProperty("name").toString() + " --- " + os.getType().name() 
                    + " ---> " + os.getEndNode().getProperty("name").toString());
            Object num = null;
            if (os.getAllProperties().keySet().contains("typeReportRelation"))
                num = os.getEndNode().getProperty("ns0__num");
            if (num==null || Integer.valueOf(num.toString())<3)
                    hasPreviusSentence1.remove(os);
        }
        for (var ha : hasAccomplice1){
            log.info("\t\tArticle235Based " +ha.getStartNode().getProperty("name").toString() + " --- " + ha.getType().name() 
                    + " ---> " + ha.getEndNode().getProperty("name").toString());
            Object age = null;
            if (ha.getAllProperties().keySet().contains("typeReportRelation"))
                age = ha.getEndNode().getProperty("ns0__Age");
            if (age==null || Integer.valueOf(age.toString())>15)
                    hasAccomplice1.remove(ha);
        }
        //Add probabilities factor
        int size = !hasThingCharacteristic.isEmpty()? hasThingCharacteristic.size() : 0;
        size = size + (!hasOffenceAggravatingFactor.isEmpty()? hasOffenceAggravatingFactor.size() : 0);
        size = size + (!hasPreviusSentence1.isEmpty()? hasPreviusSentence1.size() : 0);
        size = size + (!hasAccomplice1.isEmpty()? hasAccomplice1.size() : 0);  
        size = size + (!belongsToCriminalOrganization1.isEmpty()? belongsToCriminalOrganization1.size() : 0);
        if(!hasThingCharacteristic.isEmpty()) {
            setProbabilityElementFactorAndTypeRel (hasThingCharacteristic, 7, 1.0/size, "necessary");            
            relation.addAll(hasThingCharacteristic);
        }
        if(!hasOffenceAggravatingFactor.isEmpty()) {
            setProbabilityElementFactorAndTypeRel (hasOffenceAggravatingFactor, 7, 1.0/size, "necessary");
            relation.addAll(hasOffenceAggravatingFactor);
        }
        if(!hasPreviusSentence1.isEmpty()) {
            setProbabilityElementFactorAndTypeRel (hasPreviusSentence1, 7, 1.0/size, "necessary");
            relation.addAll(hasPreviusSentence1);
        }
        if(!hasAccomplice1.isEmpty()) {
            setProbabilityElementFactorAndTypeRel (hasAccomplice1, 7, 1.0/size, "necessary");
            relation.addAll(hasAccomplice1);
        }
        if(!belongsToCriminalOrganization1.isEmpty()) {
            setProbabilityElementFactorAndTypeRel (belongsToCriminalOrganization1, 7, 1.0/size, "necessary");
            relation.addAll(belongsToCriminalOrganization1);
        }
        if(size == 0 && creation) {
            log.info("\tCreate node with relationType: " + "ns0__hasThingCharacteristic");
        Node o = tx.createNode(Label.label("ThingCharacteristic"));
        o.setProperty("name", "no_name");
        Relationship r = n.createRelationshipTo(o, RelationshipType.withName("ns0__hasThingCharacteristic"));
        setTypeReportRelation(r, "created");
        relation.add(r);
        }
        if(size == 1 && article.endsWith("_2")) {
            //log.info("\tCreate node with relationType: " + "ns0__hasThingCharacteristic");
        Node o = tx.createNode(Label.label("ThingCharacteristic"));
        o.setProperty("name", "no_name2");
        Relationship r = n.createRelationshipTo(o, RelationshipType.withName("ns0__hasThingCharacteristic"));
        setTypeReportRelation(r, "created");
        relation.add(r);
        }
        
    }
    
    
    
    public static class RelationshipProbabilities {
        // These records contain two lists of distinct relationship types going in and out of a Node.
        public List<Relationship> relations;
//        public List<String> probabilities;

        public RelationshipProbabilities(List<Relationship> relations, List<String> probabilities) {
            this.relations = relations;
//            this.probabilities = probabilities;
        }
    }
}

