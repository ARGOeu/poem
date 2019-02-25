import React, { Component } from 'react';
//import './App.css';
import { Formik, Field, FieldArray, Form } from 'formik';

const token = "TOKEN"
const id_profile="ID_PROFILE"

const MetricProfileAPI = 'https://web-api-devel.argo.grnet.gr/api/v2/metric_profiles'
const AggregationProfileAPI = 'https://web-api-devel.argo.grnet.gr/api/v2/aggregation_profiles/'


class App extends Component {
  constructor(props) {
    super(props)
    this.state = {
      loading: false,
      aggregation_profile: {},
      metric_profile: {},
      list_metric_profiles: {},
    }
    this.fetchMetricProfiles = this.fetchMetricProfiles.bind(this)
    this.fetchAggregationProfile = this.fetchAggregationProfile.bind(this)
    this.extractListOfMetricsProfiles = this.extractListOfMetricsProfiles.bind(this)
    this.onMetricProfileChange = this.onMetricProfileChange.bind(this)

    this.logic_operations = ["OR", "AND", null] 
    this.endpoint_groups = ["servicegroups", "sites"]
    this.headers = {"Accept": "application/json", "x-api-key": token}
  }

  fetchMetricProfiles() {
    return fetch(MetricProfileAPI, 
      {headers: this.headers})
      .then(response => response.json())
      .then(json => json['data']) 
      .catch(err => console.log('Something went wrong: ' + err))
  }

  fetchAggregationProfile(idProfile) {
    return fetch(AggregationProfileAPI + idProfile, 
      {headers: this.headers})
      .then(response => response.json())
      .then(json => json['data'])
      .then(array => array[0])
      .catch(err => console.log('Something went wrong: ' + err))
  }

  onMetricProfileChange(event) {
    let selected_profile = {name: event.target.value}
    let list_services = this.extractListOfServices(selected_profile,
                                                   this.state.list_metric_profiles)
    this.setState({list_services: list_services})
  }

  extractListOfMetricsProfiles(allProfiles) {
    var list_profiles = []

    allProfiles.forEach(profile => {
      var i = list_profiles['length']
      var {name, id} = profile

      list_profiles[i] = {name, id}
      i += 1
    })

    return list_profiles
  }

  extractListOfServices(profileFromAggregation, listMetricProfiles)
  {
    let targetProfile = listMetricProfiles.filter(p => p.name === profileFromAggregation.name)

    let list_services = targetProfile[0].services.map(s => s.service)
    list_services[list_services['length']] = null

    return list_services 
  }

  componentWillMount() {
    this.setState({loading: true})

    Promise.all([this.fetchAggregationProfile(id_profile), this.fetchMetricProfiles()])
      .then(([aggregp, metricp]) => this.setState(
        {
          aggregation_profile: aggregp, 
          list_metric_profiles: metricp,
          list_services: this.extractListOfServices(aggregp.metric_profile, metricp),
          loading: false
        }))
  }

  render() {
    const {aggregation_profile, list_metric_profiles, list_services, loading} = this.state

    return (
      <div className="App">
        { 
          (loading) ? 
            <div>Loading profiles...</div> : 
            (!aggregation_profile && !list_metric_profiles && !list_services) ?
              <div>No profile loaded</div> :
              <Formik
                initialValues={{
                  name: aggregation_profile.name, 
                  metric_operation: aggregation_profile.metric_operation,
                  profile_operation: aggregation_profile.profile_operation,
                  metric_profile: aggregation_profile.metric_profile.name,
                  endpoint_group: aggregation_profile.endpoint_group,
                  groups: aggregation_profile.groups
                }}  
                onSubmit = {(values, actions) => alert(JSON.stringify(values, null, 2))}
                render = {props => (
                  <Form>
                    <section>
                      <p>
                        <label>Aggregation profile: </label>
                        <Field type="text" name="name"/>
                      </p>
                      <p>
                        <label>Metric operation: </label>
                        <Field 
                          name="metric_operation" 
                          component={DropDown} 
                          data={this.logic_operations}/> 
                      </p>
                      <p>
                        <label>Profile operation: </label>
                        <Field 
                          name="profile_operation" 
                          component={DropDown} 
                          data={this.logic_operations}/> 
                      </p>
                      <p>
                        <label>Metric profile: </label>
                        <Field 
                          name="metric_profile" 
                          component={DropDown} 
                          data={list_metric_profiles.map(e => e.name)}
                          onChange={this.onMetricProfileChange}/> 
                      </p>
                      <p>
                        <label>Endpoint group: </label>
                        <Field 
                          name="endpoint_group" 
                          component={DropDown} 
                          data={this.endpoint_groups}/> 
                      </p>
                      <FieldArray
                        name="groups"
                        render={props => (
                          <GroupList
                            {...props}
                            list_services={list_services}
                            list_operations={this.logic_operations}
                          />)}
                      />
                    </section>
                    <button type="submit">Save</button>
                  </Form>
                )}
              />
        }
      </div>
    );
  }
}

const DropDown = ({field, data=[], placeholder="----------", prefix=""}) => 
  <Field component="select"
    name={prefix ? `${prefix}.${field.name}` : field.name} 
    text={field.value}
    placeholder={placeholder}> 
    {data.map((name, i) =>
      <option key={i} text={name}>{name}</option>
    )}
  </Field>

const GroupList = ({name, form, list_services, list_operations}) =>
  <div className="groups">
    { (form.values.groups.length === 0) ?
          <p>No Groups listed. (Add a group)</p> :
          form.values[name].map((group, i) =>
            <FieldArray
              key={i}
              name="groups"
              render={props => (
                <Group
                  {...props}
                  key={i}
                  operation={group.operation}
                  services={group.services}
                  list_services={list_services}
                  list_operations={list_operations}
                  groupindex={i}
                  last={i === form.values[name].length - 1}
                />
              )}
            />
        )
    }
  </div>

const Group = ({name, operation, services, list_operations, list_services, form, groupindex, remove, push, last}) =>
  <div className={`groups.${groupindex}`} key={groupindex}>
      <Field
        name={`groups.${groupindex}.name`}> 
      </Field>
      <DropDown 
        field={{name: "operation", value: operation}}
        data={list_operations}
        prefix={`groups.${groupindex}`}
      />
      <button
        type="button"
        onClick={() => remove(groupindex)}
      >
        -
      </button>
      { (last) ?
          <div className="group-add">
            <button
              type="button"
              onClick={() => push({name: '-----------', 
                                   operation: '----',
                                   services: [{name: '-----------', 
                                              operation: '----'}]})}
            >
              Add new group
            </button>
          </div> :
          null 
      }
      <FieldArray
        name={`groups.${groupindex}`}
        render={props => (
          <ServiceList
            list_services={list_services}
            list_operations={list_operations}
            services={services}
            groupindex={groupindex}
            form={form}
          />)}
      />
  </div>

const ServiceList = ({services, list_services=[], list_operations=[], groupindex, form}) =>
  <div className="services">
    { (services.length === 0) ?
        <p>No Services listed. (Add a service)</p> :
        services.map((service, i) =>
          <FieldArray
            key={i}
            name={`groups.${groupindex}.services`}
            render={props => (
              <Service
                {...props}
                key={i}
                operation={service.operation} 
                list_services={list_services} 
                list_operations={list_operations} 
                groupindex={groupindex}
                index={i}
                last={i === services.length - 1}
              />
            )}
          />
        )
    }
  </div>

const Service = ({name, operation, list_services, list_operations, groupindex, index, remove, push, last}) => 
  <div className={`services.${index}`}>
    <DropDown 
      field={{name: "name", value: name}}
      data={list_services} 
      prefix={`groups.${groupindex}.services.${index}`}
    />
    <DropDown 
      field={{name: "operation", value: operation}}
      data={list_operations}
      placeholder="OPERATION"
      prefix={`groups.${groupindex}.services.${index}`}
    />
    <button
      type="button"
      onClick={() => remove(index)}
    >
      -
    </button>
    { (last) ?
        <div className="services-add">
          <button
            type="button"
            onClick={() => push({name: '-----------', operation: ''})}
          >
            Add new service
          </button>
        </div> :
        null
    }
  </div>


export default App;
